# coding: utf-8

""" Diganostic plotting for SMH sessions """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ["MeasurementsPlotDialog", "show_emp_summary", "EMPSummaryDialog", "SNRSpectrumDialog"]

from ..core import *
from ..specutils import Spectrum1D

from gui_core import *
from matplotlib.gridspec import GridSpec


class MeasurementsPlotDialog(HasTraits):
    """ Dialog to show atomic line measurements """

    x_axis_options = List
    x_axis = Enum(values='x_axis_options')

    x_bound_min = Float
    x_bound_max = Float
    y_bound_min = Float
    y_bound_max = Float
    bound_rescale = Button("Re-scale")

    y_axis_options = List
    y_axis = Enum(values='y_axis_options')
    display_linear_trend = Bool(True)

    # Plot
    display = Instance(Figure)

    view = View(
        Item('display', editor=MPLFigureEditor(), show_label=False, resizable=True),
        VGroup(
            Item('x_axis', label='X-axis', padding=5),
            Item('y_axis', label='Y-axis', padding=5),
            HGroup(
                Item('display_linear_trend', show_label=False),
                Label('Display linear trend line'),
                spring),
            HGroup(
                Item('x_bound_min', label='X bounds', padding=5, format_str="%1.2e"),
                Item('x_bound_max', show_label=False, padding=5, format_str="%1.2e"),
                spring,
                Item('bound_rescale', show_label=False, padding=5),
                ),
            HGroup(
                Item('y_bound_min', label='Y bounds', padding=5, format_str="%1.2e"),
                Item('y_bound_max', show_label=False, padding=5, format_str="%1.2e"),
                spring
                ),
            ),
        buttons=['OK'],
        title='Plot Measurement Properties',
        resizable=True,
        height=700,
        width=600,
        )

    def __init__(self, measurements):
        HasTraits.__init__(self)

        self._axis_options = {
            # Name: (key, label, )
            'Rest wavelength':          ('rest_wavelength', 'Wavelength, $\lambda$ ($\AA{}$)', ),
            'Measured wavelength':      ('measured_wavelength', 'Wavelength, $\lambda$ ($\AA{}$)', ),
            'Equivalent width':         ('measured_equivalent_width', 'Equivalent Width (m$\AA{}$)', ),
            'Transition':               ('transition', 'Transition', ),
            'Excitation potential':     ('excitation_potential', 'Excitation Potential (eV)', ),
            'Oscillator strength':      ('oscillator_strength', '$\log{gf}$'),
            'Measured FWHM':            ('measured_fwhm', 'FWHM ($\AA{}$)', ),
            'Measured trough':          ('measured_trough', 'Trough Point Flux', ),
            'Measured chi-squared':     ('measured_chi_sq', '$\chi^2$', ),
            'Measured line velocity':   ('measured_line_velocity', 'Line Velocity, $V_{line}$ (km s$^{-1}$)', ),
            'Detection sigma':          ('detection_sigma', 'Line Detection Significance, $\sigma_{line}$', ),
            'Abundance':                ('abundance', 'Line Abundance, $\log{\epsilon}$', ),
            'Delta abundance':          ('delta_abundance', 'Delta Line Abundance, $\delta\log{\epsilon}$', ),
            'Reduced equivalent width': ('reduced_equivalent_width', 'Reduced Equivalent Width, $\log{{EW}/\lambda_0}$', ),
            'Minimum detectable EW':    ('minimum_detectable_ew', 'Minimum Detectable Equivalent Width (m$\AA{}$)', ),
        }

        self.x_axis_options = self._axis_options.keys()
        self.y_axis_options = self._axis_options.keys()

        # Build array?
        self._column_indices = ('rest_wavelength measured_wavelength measured_equivalent_width transition excitation_potential '
            'oscillator_strength measured_fwhm measured_trough measured_chi_sq measured_line_velocity detection_sigma '
            'abundance delta_abundance reduced_equivalent_width minimum_detectable_ew').split()

        num_columns = len(self._column_indices) + 1 # one for is_acceptable as well
        self.measurements = np.zeros((len(measurements), num_columns))
        for i, measurement in enumerate(measurements):

            row = []
            for j, key in enumerate(self._column_indices):
                row.append(getattr(measurement, key))
            self.measurements[i, 0] = int(measurement.is_acceptable)
            self.measurements[i, 1:] = row

    @on_trait_change('x_axis,y_axis,display_linear_trend')
    def update_plot(self):
        """ Update the plot """
        
        x_axis_key, x_axis_label = self._axis_options[self.x_axis]
        y_axis_key, y_axis_label = self._axis_options[self.y_axis]

        x_axis_index = self._column_indices.index(x_axis_key) + 1 # Account for column zero being is_acceptable
        y_axis_index = self._column_indices.index(y_axis_key) + 1 # Account for column zero being is_acceptable

        x_axis_data = self.measurements[:, x_axis_index]
        y_axis_data = self.measurements[:, y_axis_index]

        acceptable_point_indices = np.where(self.measurements[:, 0] > 0)
        
        # I'm sorry
        x_axis_data = x_axis_data[acceptable_point_indices]
        y_axis_data = y_axis_data[acceptable_point_indices]

        finite_point_indices = np.isfinite(x_axis_data)
        x_axis_data = x_axis_data[finite_point_indices]
        y_axis_data = y_axis_data[finite_point_indices]

        finite_point_indices = np.isfinite(y_axis_data)
        x_axis_data = x_axis_data[finite_point_indices]
        y_axis_data = y_axis_data[finite_point_indices]

        if len(x_axis_data) * len(y_axis_data) == 0:
            return None

        A = np.vstack([x_axis_data, np.ones(len(x_axis_data))]).T
        m, c = np.linalg.lstsq(A, y_axis_data)[0]

        ax = self.display.axes[0]

        ax.set_xlabel(x_axis_label)
        ax.set_ylabel(y_axis_label)
        
        if hasattr(self, '_display_acceptable_points'):
            self._display_acceptable_points.set_offsets(np.vstack([
                x_axis_data,
                y_axis_data
                ]).T)

        else:
            self._display_acceptable_points = ax.scatter(x_axis_data, y_axis_data, marker='o', facecolor='none', edgecolor='k')

        scale = (0.95, 1.05)
        x_finite_data = x_axis_data[np.isfinite(x_axis_data)]

        x_bounds = np.array([np.min(x_finite_data), np.max(x_finite_data)])

        x_bounds[0] *= scale[0] if x_bounds[0] > 0 else scale[1]
        x_bounds[1] *= scale[0] if x_bounds[1] < 0 else scale[1]

        y_finite_data = y_axis_data[np.isfinite(y_axis_data)]
        y_bounds = [np.min(y_finite_data), np.max(y_finite_data)]

        y_bounds[0] *= scale[0] if y_bounds[0] > 0 else scale[1]
        y_bounds[1] *= scale[0] if y_bounds[1] > 0 else scale[1]

        if self.display_linear_trend and np.all(np.isfinite(x_bounds)) and np.all(np.isfinite([m, c])):
            if hasattr(self, '_display_trend'):
                self._display_trend[0].set_data(x_bounds, m * x_bounds + c)

            else:
                self._display_trend = ax.plot(x_bounds, m * x_bounds + c, 'k:')

        else:
            if hasattr(self, '_display_trend'):
                self._display_trend[0].set_data([], [])

        self.x_bound_min = x_bounds[0]
        self.x_bound_max = x_bounds[1]
        self.y_bound_min = y_bounds[0]
        self.y_bound_max = y_bounds[1]
        self._bound_rescale_fired(True)


    def _bound_rescale_fired(self, value):

        ax = self.display.axes[0]
        ax.set_xlim((self.x_bound_min, self.x_bound_max))
        ax.set_ylim((self.y_bound_min, self.y_bound_max))

        if self.display.canvas is not None:
            wx.CallAfter(self.display.canvas.draw)


    def _display_default(self):
        """ Initialises the spectrum display """
        
        figure = Figure()
        figure.add_subplot(111)
        
        ax = figure.axes[0]
        
        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor('w')
        
        return figure



def show_emp_summary(session, figure):
    """ Plots a EMP summary diagnostic page for the session provided """

    if not hasattr(session, "rest_spectrum") or session.rest_spectrum is None:
        raise KeyError("no rest spectrum present in the provided session")

    # Establish axes
    gs = GridSpec(4, 2)
    gs.update(top=0.77)
    ax_hbeta = figure.add_subplot(gs.new_subplotspec((0, 0), rowspan=2))
    ax_halpha = figure.add_subplot(gs.new_subplotspec((0, 1), rowspan=2))
    ax_mg = figure.add_subplot(gs.new_subplotspec((2, 0), colspan=2))
    ax_ch = figure.add_subplot(gs.new_subplotspec((3, 0)))
    ax_eu = figure.add_subplot(gs.new_subplotspec((3, 1)))

    # Draw labels
    figure.text(0.45, 0.03, 'Wavelength, $\lambda$ ($\AA{}$)')
    figure.text(0.03, 0.55, 'Flux, $F_{\lambda}$', rotation=90)

    mag_colors, stel_pars, carbon_abun = 'None', 'None', 'None'
    stel_pars = "\t$T_{{\\rm eff}}$ = {teff:.0f}\n\t$v_t$ = {xi:.2f} km/s\n\t$\log{{g}}$ = {logg:.2f}\n\t$$[Fe/H] = ${feh:.2f}$".format(
        teff=session.stellar_teff, logg=session.stellar_logg, xi=session.stellar_vt, feh=session.stellar_feh)

    # Load the reference spectra
    spectra_dir = "data/spectra"
    spectra_filenames = ("hd140283.fits", "g64-12.fits", "hd122563.fits", \
        "cd-38_245.fits", "cs22892-52.fits", "he1523-0901.fits")

    spectra = {}
    for spectra_filename in spectra_filenames:
        full_filename = os.path.join("smh/data/spectra", spectra_filename)
        if not os.path.exists(full_filename):
            logger.warn("Could not find spectrum data file {0}".format(full_filename))
            continue

        spectra[spectra_filename] = Spectrum1D.load(full_filename)

    #Add information from headers and about star:    
    ut_date = session.rest_spectrum.headers['UT-DATE'] if session.rest_spectrum.headers.has_key('UT-DATE') else 'None'
    observer = session.rest_spectrum.headers['OBSERVER'] if session.rest_spectrum.headers.has_key('OBSERVER') else 'None'
    star_name = session.rest_spectrum.headers['OBJECT'] if session.rest_spectrum.headers.has_key('OBJECT') else 'Input Star'
    t_exp = session.rest_spectrum.headers['EXPTIME'] if session.rest_spectrum.headers.has_key('EXPTIME') else 'None'
    slit = session.rest_spectrum.headers['SLITSIZE'] if session.rest_spectrum.headers.has_key('SLITSIZE') else 'None'

    #t_exp is a float
    figure.text(0.1, 0.95, 'Name: ' + star_name)
    figure.text(0.1, 0.92, 'Stellar parameters: ' + '\n' + stel_pars, verticalalignment="top")
    figure.text(0.4, 0.95, 'Exposure time: ' + str(t_exp))
    figure.text(0.4, 0.92, 'Slit: ' + slit)
    figure.text(0.4, 0.89, 'UT Date: ' + ut_date)
    figure.text(0.4, 0.86, 'Observer: ' + observer)

    #Place separate x and y limits on each plot to show the region of interest
    #Add label to each plot
    ax_hbeta.set_xlim(4858.33, 4864.33)
    ax_hbeta.set_ylim(0, 1.2)
    ax_hbeta.set_xticks(np.arange(4859, 4864, 2))
    #change number of ticks on the x-axis
    ax_hbeta.annotate('H-$\\beta$', xy=(4861.33, 0.2), xytext=(25, -10), textcoords='offset points')

    ax_halpha.set_xlim(6559.8, 6565.8)
    ax_halpha.set_ylim(0, 1.2)
    ax_halpha.set_xticks(np.arange(6560,6565, 2))
    ax_halpha.annotate('H-$\\alpha$', xy=(6562.8, 0.2), xytext=(15, -10), textcoords='offset points')

    ax_mg.set_xlim(5163, 5187)
    ax_mg.set_ylim(0.2, 1.4)
    ax_mg.annotate('Mg', xy=(5175, 1.0), xytext=(40, -50), textcoords='offset points') 

    ax_ch.set_xlim(4305, 4317)
    ax_ch.set_ylim(0, 1.5)
    ax_ch.annotate('CH', xy=(4312, 1.0), xytext=(-20, 10), textcoords='offset points')
    ax_ch.hlines(1.0,4300, 4320, linestyle = '--')
    #draw dashed line at 1.0 to indicate solar aubndance

    ax_eu.set_xlim(4127, 4131)
    ax_eu.set_ylim(0, 1.4)
    ax_eu.set_xticks(np.arange(4127, 4133, 2)) #TODO
    ax_eu.annotate('Eu', xy = (4129, 1.0), xytext=(50,10), textcoords='offset points')

    #add literature and determinedtemperatres to H_beta plot
    temp_lit = [['$T_{\\rm lit}$', 'k'], ['4600', 'b'],['4630', 'r'], ['4800', 'g'], ['5650', 'm'], ['6450', 'c']]
    temp_eff = [['$T_{\\rm eff}$', 'k'], ['4350', 'b'],['4370', 'r'], ['4620', 'g'], ['5550', 'm'], ['6430', 'c']]
    coord = 100
    for entry in temp_lit:
        ax_hbeta.annotate(entry[0], xy=(4858.33, 0), xytext=(40, coord),
            textcoords='offset points', size=10, color=entry[1])
        coord = coord - 15

    coord = 100
    for entry in temp_eff:
        ax_hbeta.annotate(entry[0], xy=(4858.33, 0), xytext=(270, coord),
            textcoords='offset points', size=10, color=entry[1])
        coord = coord - 15


    all_plots=[ax_hbeta, ax_halpha, ax_mg, ax_ch, ax_eu]
    for subplot in all_plots:
        specline = subplot.plot(
            session.rest_spectrum.disp,
            session.rest_spectrum.flux,
            c='k', linewidth=2)

        #get values of x-ticks
        subplot.set_xticklabels(['%i' % tick for tick in subplot.get_xticks()])
        #add the values (to avoid scientific notation)

    if "cd-38_245.fits" in spectra:
        cd_38_245_line = ax_mg.plot(spectra["cd-38_245.fits"].disp, spectra["cd-38_245.fits"].flux, c = 'y')

    if "cs22892-52.fits" in spectra:
        cs22892_52_line = ax_mg.plot(spectra["cs22892-52.fits"].disp, spectra["cs22892-52.fits"].flux, c='g')
        cs22892_52_line = ax_ch.plot(spectra["cs22892-52.fits"].disp, spectra["cs22892-52.fits"].flux, c='g')

    if "he1523-0901.fits" in spectra:
        he1523_0901_line = ax_eu.plot(spectra["he1523-0901.fits"].disp, spectra["he1523-0901.fits"].flux, c='r')
    
    hyd_plots = [ax_hbeta, ax_halpha]
    spectra_to_plot_for_hydrogen_lines = ["hd140283.fits", "g64-12.fits", "hd122563.fits",\
    "cs22892-52.fits", "he1523-0901.fits"]

    legend_plots = [specline]
    legend_labels = [star_name]

    for i, subplot in enumerate(hyd_plots):

        colors = ("m", "c", "b", "g", "r")
        for color, spectra_to_plot in zip(colors, spectra_to_plot_for_hydrogen_lines):
            if spectra_to_plot in spectra:

                spectrum = spectra[spectra_to_plot]
                line_plot = subplot.plot(spectrum.disp, spectrum.flux, c=color)

                if i == 0:
                    legend_plots.append(line_plot)
                    legend_labels.append(spectra_to_plot.rstrip(".fits").upper())
        
    #Add legend to upper right corner of figure
    figure.legend(legend_plots, legend_labels, (.7, .8), prop = {'size': 12})

    return figure



class EMPSummaryDialog(HasTraits):
    """ A dialog to show the EMP summary diagnostic plots """

    figure = Instance(Figure)
    view = View(
        Item("figure", editor=MPLFigureEditor(), show_label=False),
        buttons=["OK"],
        title="EMP Summary",
        resizable=True,
        height=750,
        width=1050
        )

    def __init__(self, session):
        self.session = session

    def _figure_default(self):
        """ Initialise the default figure """

        figure = Figure()
        figure.subplots_adjust(left=0.10, right=0.95)
        rect = figure.patch
        rect.set_facecolor("w")
        figure = show_emp_summary(self.session, figure)

        return figure


class SNRSpectrumDialog(HasTraits):

    snr_spectrum = Instance(Spectrum1D)
    display = Instance(Figure)

    view = View(
        Item('display', editor=MPLFigureEditor(), show_label=False, resizable=True),
        buttons=['OK'],
        title='SNR Spectrum',
        height=400,
        width=700,
        resizable=True
        )

    def _display_default(self):
        """Initialises the spectrum display."""
        
        figure = Figure()
        figure.subplots_adjust(left=0.10, bottom=0.15, right=0.95)
        ax = figure.add_subplot(111)
        ax.set_xlabel('Wavelength, $\lambda$ ($\AA{}$) ', fontsize=11)
        ax.set_ylabel('Signal-to-Noise',fontsize=11)
        rect = figure.patch
        rect.set_facecolor('w')
        return figure


    def __init__(self, spectrum):
        self.snr_spectrum = spectrum

    def _snr_spectrum_changed(self, spectrum):
        self.display.axes[0].plot(spectrum.disp, spectrum.flux, 'k')
        self.display.axes[0].set_xlim(spectrum.disp[0], spectrum.disp[-1])
        self.display.axes[0].set_ylim(0, np.max(spectrum.flux) * 1.2)

        if self.display.canvas is not None:
            wx.CallAfter(self.display.canvas.draw)
