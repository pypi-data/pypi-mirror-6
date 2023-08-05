# coding: utf-8

""" Database functionality for the Spectroscopy Made Hard GUI """

__author__ = "Andy Casey <andy@astrowizici.st>"

# Standard Libraries
import traceback
from datetime import datetime

# Module imports
from core import *
from session import AnalysisSession

try:
    import psycopg2

except ImportError:
    logging.warn("Could not load the psycopg2 module. No session information can be transmitted to external databases.")
    PSYCOPG2_AVAILABLE = False

else:
    PSYCOPG2_AVAILABLE = True

    import psycopg2.extras


__all__ = ["DatabaseConnectionGUI", "PSYCOPG2_AVAILABLE"]


class QuestionHandler(Handler):
	def yes(self, info):
		info.ui.owner.close(info, True)
		return True

	def no(self, info):
		info.ui.owner.close(info, False)
		return False


class Question(HasTraits):
    """ GUI class to ask a confirmation question """

    answer = Bool(False)
    message = Str

    yes = Button('Yes')
    no = Button('No')

    view = View(
        Item('message', show_label=False, padding=10, style='readonly'),
        handler=QuestionHandler(),
        title='Confirm',
        buttons=[Action(name='Yes', action='yes'), Action(name='No', action='no')]
        )

    def _no_fired(self, value):
        self.answer = False

    def _yes_fired(self, value):
        self.answer = True


class ConnectionInformation(HasTraits):
    """ GUI class to display a connection message """

    message = Str

    view = View(
        Item('message', show_label=False, padding=10, style='readonly'),
        title='Information',
        buttons=['OK']
        )


class Database:

    def __init__(self, host=None, port=5432, user=None, password=None, database=None):

        try:
            self.connection = psycopg2.connect(host=host, port=port, user=user, password=password, database=database)
        
        except Exception as err:

            dialog = ConnectionInformation()
            dialog.message = err.__str__()
            dialog.configure_traits()

            etype, value, tb = sys.exc_info()

            logging.critical(("Database connection failed. Traceback (most recent call last):\n"
                              "%s\t\n"
                              "%s: %s") % ("\n".join(traceback.format_tb(tb, 5)), etype, value))

        else:
            # Connection has been made, let's get a cursor
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


        return None

    def update_analysis_results(self, info, prime_key):
    	"""Updates the database analysis table with the results from this session."""

    	# Delete the existing one
    	query = self.query('delete from analysis_results where prime_key = %s and "Author" = %s', [prime_key, info.object.username.lower()])
    	self.connection.commit()

    	self.insert_analysis_results(info, prime_key)


    def insert_analysis_results(self, info, prime_key):
        """Inserts the current analysis information to the analysis table."""

        analysis = {
            'prime_key':	prime_key,
            'star_name':    info.object.session.headers['OBJECT'],
            'Vr':           info.object.session.v_helio,
            'Vr_error':		info.object.session.v_err,
            'Teff':         info.object.session.stellar_teff,
            'log_g':        info.object.session.stellar_logg,
            'v_t':          info.object.session.stellar_vt,
            '[M/H]':        info.object.session.stellar_feh,
            'Author':       info.object.username.lower(),
        } 

        # Append elemental abundance measurements to analysis if they exist.
        element_columns_in_table = ('Fe I', 'Fe II', 'Na I', 'Mg I', 'Al I', 'Si I', 'Ca I', 'Sc I', 'Sc II', 'Ti I', 'Ti II', 'V I', 'Cr I', 'Mn I', 'Co I', 'Ni I', 'Zn I')

        for element_measurement in info.object.session.elemental_abundances:
            if element_measurement.element in element_columns_in_table:
                # Get a small string representation for the element
                element_str = element_measurement.element.replace(' ', '')

                analysis['log_eps(%s)' % (element_str, )] = element_measurement.abundance_mean
                analysis['sd_%s' % (element_str, )] = element_measurement.abundance_std
                analysis['N_%s' % (element_str, )] = element_measurement.number_of_lines

        # Build the string
        query_string = "insert into analysis_results (\"%s\") values (%s)" \
        % ('", "'.join(analysis.keys()), ', '.join(['%s'] * len(analysis.keys())), )

        query = self.query(query_string, analysis.values())
        self.connection.commit()

        return True



    def insert_observing_information(self, info):
        """Inserts the current session information to the observing log."""

        star_name     = info.object.session.headers['OBJECT']
        ra             = info.object.session.headers['RA-D']
        dec            = info.object.session.headers['DEC-D']
        ut_date     = datetime.fromtimestamp(mktime(strptime(info.object.session.headers['UT-DATE'] + ' ' + info.object.session.headers['UT-START'], '%Y-%m-%d %H:%M:%S')))
        exptime     = info.object.session.headers['EXPTIME']
        observer    = info.object.session.headers['OBSERVER']
        slitsize    = info.object.session.headers['SLITSIZE'] if info.object.session.headers.has_key('SLITSIZE') else info.object.session.headers['COMMENT']
        comments    = info.object.session.headers['COMMENT'] if info.object.session.headers.has_key('COMMENT') and len(info.object.session.headers['COMMENT']) > 0 else None
        airmass        = info.object.session.headers['AIRMASS']


        query = self.query(("insert into observing_log"
            "(star_name, ra, dec, ut_date, exptime, observer, slitsize, comments, airmass)"
            " values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning prime_key"),
            [star_name, ra, dec, ut_date, exptime, observer, slitsize, comments, airmass])

        prime_key = query.fetchone()[0]
        self.connection.commit()

        return prime_key


    def query(self, sql, sql_args=[]):
        """Query adapter to log and perform PostGreSQL queries"""
        
        cursor = self.cursor

        try:
            logging.debug("SQL query initialised: %s with arguments %s" % (sql, sql_args,))
            sql_query = cursor.execute(sql, sql_args)
        
        except psycopg2.Error as e:
            logging.warn('SQL query failed "%s (%s)": %s with arguments %s' % (e.args, e.pgerror, sql, sql_args))
            cursor.connection.rollback()
        
        else:
            logging.debug("SQL:\t" + sql % tuple(sql_args))
       
        return cursor
            


    def get_primary_key(self, info):
        """Checks to see if the star exists in the observing log.

        Returns either a primary key, or False."""

        star_name = info.object.session.headers['OBJECT']
        ut_date = datetime.fromtimestamp(time.mktime(time.strptime(info.object.session.headers['UT-DATE'] + ' ' + info.object.session.headers['UT-START'], '%Y-%m-%d %H:%M:%S')))
        exptime = info.object.session.headers['EXPTIME']

        query = self.query('select * from observing_log where star_name = %s and ut_date = %s and exptime = %s',
            [star_name, ut_date, exptime])

        if query.rowcount == 0:
            return False

        prime_key = query.fetchone()['prime_key']

        return prime_key


    def get_analysis_results(self, info, prime_key):
    	"""Checks to see if this star has been analysed by this author before."""

    	query = self.query('select prime_key, "Author" from analysis_results where prime_key = %s and "Author" = %s', [prime_key, info.object.username.lower()])

    	return True if query.rowcount > 0 else False


    def disconnect(self):
        self.cursor.close()
        self.connection.close()




class DatabaseHandler(Handler):

    def upload(self, info):

        if not info.initialized \
        or None in (info.object.host, info.object.port, info.object.username, info.object.password): return

    
        # Connection information
        database = Database(
            host = info.object.host.lower(),
            port = info.object.port,
            user = info.object.username.lower(),
            password = info.object.password,
            database = info.object.database_name)

        message = ''

        prime_key = database.get_primary_key(info)
        if not prime_key:
            logging.debug("Star not found in database. Adding to observing log.")

            prime_key = database.insert_observing_information(info)

            message += 'Observation details added to observing log.'

        # Has this author analysed this star before?
        analysis_already_exists = database.get_analysis_results(info, prime_key)
        if analysis_already_exists:
        	logging.debug("This user has already analysed this star. Asking to overwrite...")

        	# Ask to clobber
        	question = confirm(info.ui.control, 'You have already analysed this star before. Do you want to update the database with these results?')

        	if question == 30:
	        	message += ' The results from your analysis of this star have been updated in the database.'
	        	database.update_analysis_results(info, prime_key)

	        else:
	        	message = 'No analysis results were sent to the database.'

        else:

	        # Insert the analysis results
	        database.insert_analysis_results(info, prime_key)

	        message += ' The results from your analysis of this star have been inserted into the database.'


        dialog = ConnectionInformation()
        dialog.message = message
        dialog.configure_traits(kind='modal')

        database.disconnect()

        # Close the connection dialog
        info.ui.owner.close()



    







class DatabaseConnectionGUI(HasTraits):

    #session = Instance(AnalysisSession)

    host = Str('panda.mit.edu')
    port = Int(5432)

    username = Str
    password = Password

    database_name = Enum('SkyMapper')

    connect = Button('Upload')

    view = View(
        HGroup(

            Item('host', label='Server', padding=10),
            Item('port', label='Port', padding=10),
            ),
        Item('database_name', label='Database', padding=10),
        Item('username', label='Username', padding=10),
        Item('password', label='Password', padding=10),
        title='Connect to database',
        handler=DatabaseHandler(),
        buttons=[
            Action(name='Upload', action='upload'),
            'Cancel'
            ]
        )

    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)

        self.session = session
