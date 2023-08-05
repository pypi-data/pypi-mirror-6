# coding: utf-8

""" A bit of organisation for the SMH GUI tabs """

__author__ = "Andy Casey <andy@astrowizici.st>"

from summary import SummaryTab
from normalisation import NormalisationTab
from doppler import DopplerCorrectTab
from equivalentwidths import EquivalentWidthsTab
from stellarparameters import StellarParametersTab
from chemicalabundances import ChemicalAbundancesTab
from synthesis import SynthesisTab

__all__ = [
    "SummaryTab", "NormalisationTab", "DopplerCorrectTab", "EquivalentWidthsTab",\
    "StellarParametersTab", "ChemicalAbundancesTab", "SynthesisTab"
    ]