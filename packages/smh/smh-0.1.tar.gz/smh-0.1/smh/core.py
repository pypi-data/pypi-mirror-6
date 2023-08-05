# coding: utf-8

""" Contains core functionality required for analysis in Spectroscopy Made Hard. """

__author__ = "Andy Casey <andy@astrowizici.st>"

# Standard libraries
import json
import logging
import os
import tempfile

from time import mktime, strptime, time

# Third party libraries
import numpy as np

# Traits imports
from traits.api import \
    Any, Array, Instance, property_depends_on, Button, DelegatesTo, \
    PrototypedFrom, HasTraits, HasStrictTraits, Event, Password, Property, \
    Enum, Float, File, Str, Dict, Int, Bool, List, on_trait_change, Range

# SMH imports
import nlte
import utils

# Load solar abundances
with open(os.path.join(os.path.dirname(__file__), "../config/solar_abundances.json"), "r") as fp:
    solar_abundances = json.load(fp)
    
tempfile.tempdir = '/tmp'
logger = logging.getLogger(__name__)


# Core Traits Descriptors
class AtomicTransition(HasStrictTraits):
    
    # Line list inputs
    rest_wavelength = Float
    species = Float
    transition = Float
    excitation_potential = Float
    oscillator_strength = Float
    vanderwaal_broadening = Float
    
    comment = Str
    element = Str
    
    # Measured properties
    measured_wavelength = Float
    measured_fwhm = Float
    measured_trough = Float
    measured_equivalent_width = Float(np.NaN)
    measured_chi_sq = Float(np.NaN)
    measured_line_velocity = Float(np.NaN)

    profile = Array
    detection_sigma = Float(np.NaN)
    abundance = Float(np.NaN)
    nlte_abundance = Float(np.NaN)
    delta_abundance = Float(np.NaN)
    reduced_equivalent_width = Float(np.NaN)
    
    # Quality criteria
    is_acceptable = Bool(False)
    is_uncertain = Bool(False)
    is_blank = Str('')

    minimum_detectable_ew = Float
    
    """
    view = View(
        Item('rest_wavelength', label='Rest wavelength', padding=5),
        Item('transition', label='Transition', padding=5),
        Item('excitation_potential', label='Excitation potential', padding=5),
        Item('oscillator_strength', label='Oscillator strength', padding=5),
        title='Line transition',
        buttons=['OK', 'Cancel'])
    """


    def __init__(self, session=None, nlte_grid=None, **kwargs):
        HasTraits.__init__(self)

        if session is not None:
            self.__session__ = session

        # Has this been initialised from the GUI?
        if len(kwargs.keys()) == 0:
            is_configured = self.configure_traits(kind="modal")

            # Self destruct if we're not configured
            return None if is_configured else False

        else:
            # Set the provided attributes as expected 
            [setattr(self, k, v) for k, v in kwargs.iteritems()]
    
    def _transition_changed(self, value):
        """ Updates the element attribute once the transition has been updated """
        self.element = utils.species_to_element(value)
        self.species = value
    
    def _measured_equivalent_width_changed(self, value):
        """ Updates the reduced equivalent width when the measured equivalent width changes"""
        if self.rest_wavelength > 0:
            self.reduced_equivalent_width = np.log10((value/1000)/self.rest_wavelength)

        # These need to be re-calculated from MOOG
        self.abundance, self.nlte_abundance = np.nan, np.nan

    @on_trait_change("measured_wavelength,rest_wavelength")
    def _update_line_velocity(self):
        if self.measured_wavelength > 0 and self.rest_wavelength > 0:
            self.measured_line_velocity = 299792.458 * (1 - self.rest_wavelength/self.measured_wavelength)

    @on_trait_change("minimum_detectable_ew,measured_equivalent_width")
    def _update_detection_sigma(self):
        if  self.minimum_detectable_ew > 0 \
        and self.measured_equivalent_width > 0:
            self.detection_sigma = self.measured_equivalent_width / self.minimum_detectable_ew


class ElementalAbundance(HasTraits):
    
    species = Float
    # transition -> species
    transition = Float
    element = Str
    
    line_measurements = List(AtomicTransition)

    abundance_measurements = List(Float)
    
    abundance_mean = Float
    abundance_std = Float

    nlte_abundance_mean = Float
    nlte_abundance_std = Float
    
    number_of_lines = Int
    #uncertainty = Float
    
    solar_abundance = Float
    solar_uncertainty = Float
    
    stellar_reference_fe_h = Float
    solar_fe_abundance = Float
    
    X_on_H = Float
    X_on_Fe = Float
    X_on_Fe_uncertainty = Float

    def _transition_changed(self, value):
        self.species = value
        self.element = utils.species_to_element(value)

    @on_trait_change('abundance_mean, solar_abundance')
    def _update_x_on_h(self):
        self.X_on_H = self.abundance_mean - self.solar_abundance
    

    @on_trait_change('X_on_H, stellar_reference_fe_h')
    def _update_x_on_fe(self):
        Fe_on_H = self.stellar_reference_fe_h - self.solar_fe_abundance
        self.X_on_Fe = self.X_on_H - Fe_on_H

    @on_trait_change('number_of_lines, abundance_std')
    def _update_uncertainty(self):
        if self.number_of_lines > 0:
            self.X_on_Fe_uncertainty = self.abundance_std / np.sqrt(self.number_of_lines)
        
        else:
            self.X_on_Fe_uncertainty = np.NaN

    @on_trait_change('line_measurements.is_acceptable, line_measurements.abundance, line_measurements.nlte_abundance')
    def _update_median(self):
        
        lte_abundances = []
        nlte_abundances = []
        for line in self.line_measurements:
            if line.is_acceptable:
                if np.isfinite(line.abundance):
                    lte_abundances.append(line.abundance)
                if np.isfinite(line.nlte_abundance):
                    nlte_abundances.append(line.nlte_abundance)

        self.abundance_mean = np.mean(lte_abundances)
        self.abundance_std = np.std(lte_abundances)
        self.number_of_lines = len(lte_abundances)

        # Update the delta_abundances in the lines
        for line in self.line_measurements:
            if line.is_acceptable and np.isfinite(line.abundance):
                line.delta_abundance = line.abundance - self.abundance_mean

        self.nlte_abundance_mean = np.mean(nlte_abundances)
        self.nlte_abundance_std = np.std(nlte_abundances)
        self.nlte_number_of_lines = len(nlte_abundances)


class ElementInSynthesisSetup(HasTraits):

    highlight = Bool(False)

    atomic_number = Int
    element_repr = Str

    X_on_Fe = Float(np.nan)
    log_epsilon = Float(np.nan)
    X_on_Fe_minus_log_epsilon = Float(np.nan)

    abundance_minus_offset = Float
    abundance_plus_offset = Float
    rest_wavelengths = List(Float)

    def _atomic_number_changed(self, atomic_number):
        self.element_repr = utils.species_to_element(atomic_number).split()[0]
    
    @on_trait_change('X_on_Fe,X_on_Fe_minus_log_epsilon')
    def _update_log_epsilon(self):
        if np.all(~np.isfinite([self.log_epsilon, self.X_on_Fe])):
            return False
        self.log_epsilon = self.X_on_Fe - self.X_on_Fe_minus_log_epsilon

    @on_trait_change('log_epsilon,X_on_Fe_minus_log_epsilon')
    def _update_x_on_fe(self):
        if np.all(~np.isfinite([self.log_epsilon, self.X_on_Fe])):
            return False
        self.X_on_Fe = self.log_epsilon + self.X_on_Fe_minus_log_epsilon


    
