# Import modules required
from flask import Flask, flash, redirect, render_template, request, session, abort
import pymysql


app = Flask(__name__)                                                            #create the Flask app

class AccessDb:
    # Create a class to be used for database access
    def __init__(self):                                                          # Build the class consuctor
        self.db_con = pymysql.connect('localhost', 'root', ' ', 'Homes')       # Basic connection string
        self.db_cur = self.db_con.cursor()                                       # Get a db cursor
        self.cur_offset = 0                                                      # This class var is used to track SQL OFFSET when
        self.cur_order_by = "address"                                            # Persit the current order value
        self.cur_limit_by = 6

    def execute_query(self, query_string):                                       # Methdd used to execute SQL INSER, UPDATA and DELETE
      self.db_cur.execute(query_string)                                          # Uses pymsql execute
      self.db_con.commit()                                                       # commit CRUD actions

    def execute_list(self,query_string):                                          # Called with Select * and query offset parm
       self.db_cur.execute(query_string)                                          # Execute the Select *

       rows = self.db_cur.fetchall()                                              # Fetching all records here to a varible
       return rows                                                                # retrun the records to the caller
     # end class object blueprint


mydbobj = AccessDb()                                                              # Create an object from the class AccesDB()

# Set up the routing paths
@app.route("/")
@app.route("/home")                                                              # Path for / and /homoe use same function
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

# Route for the CRUD Demo Link on the home page See the README for details
@app.route("/crud", methods=['GET', 'POST'])
def crud():
    if request.method == 'POST':                                              # Check if this is a POST used for CRUD actions
        address = request.form['address']                                     # use FLASK request.from to capture values returnd from forms
        realtor = request.form['realtor']
        style = request.form['style']
        price = request.form['price']
        recnum = request.form['recnum']
        action = request.form['action']

        if action == 'Insert':
            dbq_string = "INSERT INTO listings (address, realtor, style, price)  Values ('%s','%s','%s', '%s')" %(address,realtor,style,price)
            mydbobj.execute_query(dbq_string)                                    # Call object execute method

        if action == 'Update':
            int(recnum)                                                           # comvert retruned char record to int for search and updating
            dbq_string = "UPDATE listings SET address='%s', realtor='%s', style='%s', price ='%s' WHERE id ='%s'"  %(address, realtor, style, price, recnum)
            mydbobj.execute_query(dbq_string)

        if action == 'Delete':  # Delete Record
            int(recnum)                                                             # comvert retruned char record to int for search and updating
            dbq_string = "DELETE FROM listings WHERE id=%s" %(recnum)
            mydbobj.execute_query(dbq_string)

        mydbobj.cur_offset = 0
        offset_var = mydbobj.cur_offset
        order_by = mydbobj.cur_order_by
        limit_by = mydbobj.cur_limit_by
        select_rows = "SELECT id, address, realtor, style, price  FROM listings  ORDER By %s  LIMIT %s  OFFSET %s " % (order_by,limit_by,offset_var)
        #args = (order_by, limit_by, offset_var)
        rows = mydbobj.execute_list(select_rows)
        return render_template('crud.html', rows=rows,)



    if request.method == 'GET':
        next_rec_set = request.args.get('next')                                       # Test for Next button - get args if key doesn't exist, returns None
        prev_rec_set = request.args.get("previous")                                   # Test for Previos  button - get args if key doesn't exist, returns None
        new_order_by = request.args.get('order_by')                                   # Test if order link was selecyrd and get parm

        if not new_order_by:
            mydbobj.cur_order_by = "address"
        else:
            mydbobj.cur_order_by = new_order_by

        if not next_rec_set and not prev_rec_set:
            mydbobj.cur_offset = 0
            offset_var = mydbobj.cur_offset
            limit_by = mydbobj.cur_limit_by
            order_by = mydbobj.cur_order_by
            select_rows = "SELECT id, address, realtor, style, price  FROM listings  ORDER By %s  LIMIT %s  OFFSET %s " % (order_by, limit_by, offset_var)
            rows = mydbobj.execute_list(select_rows)
            return render_template('crud.html', rows=rows, next_rec_set = next_rec_set, prev_rec_set= prev_rec_set,new_order_by =new_order_by      )

        elif next_rec_set:
            order_by = mydbobj.cur_order_by
            limit_by = mydbobj.cur_limit_by
            mydbobj.cur_offset = mydbobj.cur_offset +  int(next_rec_set)                   # string is being passed from from needs to be converted to int
            offset_var = mydbobj.cur_offset     # convert to string so can be concate with other string for select
            select_rows = "SELECT id, address, realtor,style, price  FROM listings  ORDER By %s  LIMIT %s  OFFSET %s" % (order_by, limit_by, offset_var)
            rows = mydbobj.execute_list(select_rows)
            return render_template('crud.html', rows=rows, next_rec_set = next_rec_set, prev_rec_set= prev_rec_set  )


        elif prev_rec_set:  # chack if next page was slected and get the parms back
            order_by = mydbobj.cur_order_by
            limit_by = mydbobj.cur_limit_by
            mydbobj.cur_offset = mydbobj.cur_offset - int(prev_rec_set)                     # string is being passed from from needs to be converted to int
            if mydbobj.cur_offset < 0:
                mydbobj.cur_offset = 0                                                      # Don't allow the offset to become a nextive interger or will crash
            offset_var = mydbobj.cur_offset
            select_rows = "SELECT id, address, realtor,style, price  FROM listings  ORDER By %s  LIMIT %s  OFFSET %s" % (order_by, limit_by, offset_var)
            rows = mydbobj.execute_list(select_rows)
            return render_template('crud.html', rows=rows, next_rec_set = next_rec_set, pre_vrec_set=prev_rec_set)

# this is just for testing
@app.route("/scroll")
def scroll():
    order_by = request.args.get('order_by')


    return render_template('scroll.html',order_by=order_by)


if __name__ == "__main__":
    app.run(debug=True)

