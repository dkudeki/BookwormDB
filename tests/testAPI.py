import unittest
import bookwormDB
import bookwormDB.CreateDatabase
import logging
import os
from subprocess import call as call
import sys

def setup_bookworm():
    """
    Creates a test bookworm. Removes any existing databases called "federalist_bookworm"
    """
    logging.info("\n\nTESTING BOOKWORM CREATION\n\n")
    import MySQLdb
    from warnings import filterwarnings
    filterwarnings('ignore', category = MySQLdb.Warning)

    import bookwormDB.configuration
    os.chdir(sys.path[0] + "/test_bookworm_files")
    bookwormDB.configuration.create(ask_about_defaults=False,database="federalist_bookworm")

    try:
        db.query("DROP DATABASE federalist_bookworm")
    except MySQLdb.OperationalError as e:
        if e[0]==1008:
            pass
        else:
            raise
    except Exception, e:
        """
        This is some weird MariaDB exception. It sucks that I'm compensating for it here.
        """
        if e[0]=="Cannot load from mysql.proc. The table is probably corrupted":
            pass
        else:
            logging.warning("Some mysterious error in attempting to drop previous iterations: just try running it again?")
            
    call(["bookworm --log-level warning build all"],shell=True,cwd=sys.path[0] + "/test_bookworm_files")


class Bookworm_SQL_Creation(unittest.TestCase):

    def test_bookworm_files_exist(self):
        bookworm = bookwormDB.CreateDatabase.BookwormSQLDatabase("federalist_bookworm")
        db = bookworm.db
        db.query("USE federalist_bookworm")
        wordCount = db.query("SELECT SUM(nwords) FROM fastcat").fetchall()[0][0]
        # This should be 212,081, but I don't want the tests to start failing when
        # we change the tokenization rules or miscellaneous things about encoding.
        self.assertTrue(wordCount>100000)
        """
        Then we test whether the API can make queries on that bookworm.
        """
        
    def test_API(self):
        from bookwormDB.general_API import SQLAPIcall as SQLAPIcall
        import json
        
        query = {
                "database":"federalist_bookworm",
                "search_limits":{},
                "counttype":"TextPercent",
                "groups":["author"],
                "method":"return_json"
        }
        
        m = json.loads(SQLAPIcall(query).execute())
        self.assertTrue(len(m)==5)

    def test_adding_metadata_to_bookworm(self):
        """
        Build out some dummy metadata: label the difference
        between even and odd paragrahs.
        """
        
        from bookwormDB.manager import BookwormManager
        manager = BookwormManager(database="federalist_bookworm")

        # Create a phony derived field to test metadata supplementing
        newMetadata = open("/tmp/test_bookworm_metadata.tsv","w")
        newMetadata.write("paragraphNumber\toddness\n")
        def even_even(number):
            if number % 2 == 0:
                return "even"
            return "odd"
                
        for n in range(500):
            newMetadata.write("%d\t%s\n" %(n,even_even(n)))


        class Dummy:
            """
            Just quickly create a namespace to stand in for the command-line args.
            """
            key = "paragraphNumber"
            format = "tsv"
            file = "/tmp/test_bookworm_metadata.tsv"
            field_descriptions = None # Test the guessing at field_descriptions while we're at it
        import os
        manager.add_metadata(Dummy)

        """
        And then we test if that can be retrieved
        """

        from bookwormDB.general_API import SQLAPIcall as SQLAPIcall
        import json
        import os
                
        query = {
                "database":"federalist_bookworm",
                "search_limits":{},
                "counttype":"TextCount",
                "groups":["oddness"],
                "method":"return_json"
        }
        SQLAPIcall(query)
        m = json.loads(SQLAPIcall(query).execute())
        # Even or odd is one of two things.
        self.assertTrue(len(m)==2)
        
        # Since the first paragraph is odd,
        # there should be more of those.
        
        self.assertTrue(m['odd'][0]>=m['even'][0])

        
"""        
class SQLConnections(unittest.TestCase):
    
        

    def test_dunning(self):
        query = {
            "database":"federalist",
            "search_limits":{"author":"Hamilton"},
            "compare_limits":{"author":"Madison"},
            "counttype":"Dunning",
            "groups":["unigram"],
            "method":"return_json"
        }
        

        try:
            #dbbindings.main(query)
            worked = True
        except:
            worked = False

        self.assertTrue(worked)
"""

        
if __name__=="__main__":
    # The setup is done without verbose logging; any failure
    # causes it to try again.
    logging.basicConfig(level=40)
    try:
        setup_bookworm()
    except:
        logging.basicConfig(level=10)
        setup_bookworm()
    logging.basicConfig(level=10)    
    unittest.main()