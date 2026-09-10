
import json
import mysql.connector

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_database_connection():

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="smart_queue_database"
    )

    return db


# =========================================================
# GET WAITING QUEUE
# =========================================================

def get_queue():

    db = get_database_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        token_id,
        customer_name,
        service,
        priority,
        status,
        created_at
    FROM queue
    WHERE status = 'Waiting'
    ORDER BY priority DESC, token_id ASC
    """

    cursor.execute(query)

    customers = cursor.fetchall()

    cursor.close()
    db.close()

    return customers


# =========================================================
# GET ALL CUSTOMERS
# =========================================================

def get_all_customers():

    db = get_database_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        token_id,
        customer_name,
        service,
        priority,
        status,
        created_at
    FROM queue
    ORDER BY priority DESC, token_id ASC
    """

    cursor.execute(query)

    customers = cursor.fetchall()

    cursor.close()
    db.close()

    return customers


# =========================================================
# GET QUEUE STATISTICS
# =========================================================

def get_statistics():

    db = get_database_connection()
    cursor = db.cursor()

    # Count waiting customers

    cursor.execute("""
        SELECT COUNT(*)
        FROM queue
        WHERE status = 'Waiting'
    """)

    waiting = cursor.fetchone()[0]

    # Count completed customers

    cursor.execute("""
        SELECT COUNT(*)
        FROM queue
        WHERE status = 'Completed'
    """)

    completed = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return {
        "waiting": waiting,
        "completed": completed
    }


# =========================================================
# GENERATE TOKEN
# =========================================================

def generate_token(customer_name, service, priority):

    db = get_database_connection()
    cursor = db.cursor()

    query = """
    INSERT INTO queue
    (
        customer_name,
        service,
        priority,
        status
    )
    VALUES
    (
        %s,
        %s,
        %s,
        'Waiting'
    )
    """

    cursor.execute(
        query,
        (
            customer_name,
            service,
            priority
        )
    )

    db.commit()

    token_id = cursor.lastrowid

    cursor.close()
    db.close()

    return token_id


# =========================================================
# GET CURRENT SERVING CUSTOMER
# =========================================================

def get_current_serving():

    db = get_database_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        token_id,
        customer_name,
        service,
        priority,
        status,
        created_at
    FROM queue
    WHERE status = 'Serving'
    ORDER BY token_id DESC
    LIMIT 1
    """

    cursor.execute(query)

    customer = cursor.fetchone()

    cursor.close()
    db.close()

    return customer


# =========================================================
# SERVE NEXT CUSTOMER
# =========================================================

def serve_next_customer():

    db = get_database_connection()
    cursor = db.cursor(dictionary=True)

    # Get the first waiting customer
    cursor.execute("""
        SELECT *
        FROM queue
        WHERE status = 'Waiting'
        ORDER BY priority DESC, token_id ASC
        LIMIT 1
    """)

    customer = cursor.fetchone()

    if not customer:

        cursor.close()
        db.close()

        return None

    # Update customer status
    cursor.execute("""
        UPDATE queue
        SET status = 'Serving'
        WHERE token_id = %s
    """, (customer["token_id"],))

    db.commit()

    cursor.close()
    db.close()

    return customer


# =========================================================
# COMPLETE CURRENT CUSTOMER
# =========================================================

def complete_current_customer():

    db = get_database_connection()
    cursor = db.cursor(dictionary=True)

    # Find the currently serving customer
    cursor.execute("""
        SELECT token_id
        FROM queue
        WHERE status = 'Serving'
        ORDER BY token_id DESC
        LIMIT 1
    """)

    customer = cursor.fetchone()

    # No customer is currently being served
    if not customer:

        cursor.close()
        db.close()

        return None

    # Change status from Serving to Completed
    cursor.execute("""
        UPDATE queue
        SET status = 'Completed'
        WHERE token_id = %s
    """, (customer["token_id"],))

    db.commit()

    cursor.close()
    db.close()

    return customer


# =========================================================
# HTTP SERVER
# =========================================================

class SmartQueueServer(BaseHTTPRequestHandler):


    # -----------------------------------------------------
    # SEND JSON RESPONSE
    # -----------------------------------------------------

    def send_json(self, data, status_code=200):

        response = json.dumps(
            data,
            default=str
        )

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        # Allow frontend to communicate with backend
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

        self.wfile.write(
            response.encode("utf-8")
        )


    # -----------------------------------------------------
    # HANDLE OPTIONS REQUEST
    # -----------------------------------------------------

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()


    # -----------------------------------------------------
    # HANDLE GET REQUEST
    # -----------------------------------------------------

    def do_GET(self):

        parsed_url = urlparse(self.path)

        path = parsed_url.path


        # ================================================
        # GET WAITING QUEUE
        # ================================================

        if path == "/api/queue":

            try:

                customers = get_queue()

                self.send_json({
                    "customers": customers
                })

            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # GET CURRENT SERVING CUSTOMER
        # ================================================

        elif path == "/api/current":

            try:

                current = get_current_serving()

                self.send_json({
                    "current": current
                })

            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # GET ADMIN DATA
        # ================================================

        elif path == "/api/admin":

            try:

                customers = get_all_customers()

                statistics = get_statistics()

                self.send_json({
                    "customers": customers,
                    "statistics": statistics
                })

            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # UNKNOWN GET URL
        # ================================================

        else:

            self.send_json(
                {
                    "error": "API endpoint not found"
                },
                404
            )


    # -----------------------------------------------------
    # HANDLE POST REQUEST
    # -----------------------------------------------------

    def do_POST(self):

        parsed_url = urlparse(self.path)

        path = parsed_url.path


        # -------------------------------------------------
        # READ REQUEST BODY
        # -------------------------------------------------

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        body = self.rfile.read(
            content_length
        )


        # Some POST requests, such as /api/serve
        # and /api/complete, do not require a body.

        if body:

            try:

                data = json.loads(
                    body.decode("utf-8")
                )

            except json.JSONDecodeError:

                self.send_json(
                    {
                        "error": "Invalid JSON data"
                    },
                    400
                )

                return

        else:

            data = {}


        # ================================================
        # GENERATE TOKEN
        # ================================================

        if path == "/api/generate":

            try:

                customer_name = data.get(
                    "customer_name"
                )

                service = data.get(
                    "service"
                )

                priority = int(
                    data.get(
                        "priority",
                        0
                    )
                )


                # Validate customer name

                if not customer_name:

                    self.send_json(
                        {
                            "error":
                            "Customer name is required"
                        },
                        400
                    )

                    return


                # Validate service

                if not service:

                    self.send_json(
                        {
                            "error":
                            "Service is required"
                        },
                        400
                    )

                    return


                # Generate token

                token = generate_token(
                    customer_name,
                    service,
                    priority
                )


                self.send_json({
                    "success": True,
                    "token": token
                })


            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # SERVE NEXT CUSTOMER
        # ================================================

        elif path == "/api/serve":

            try:

                customer = serve_next_customer()


                # No customer waiting

                if customer is None:

                    self.send_json({
                        "success": False,
                        "message":
                        "No customers are waiting."
                    })

                    return


                # Customer successfully served

                self.send_json({
                    "success": True,
                    "token":
                    customer["token_id"],
                    "customer_name":
                    customer["customer_name"],
                    "service":
                    customer["service"]
                })


            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # COMPLETE CURRENT CUSTOMER
        # ================================================

        elif path == "/api/complete":

            try:

                customer = complete_current_customer()


                # No customer currently serving

                if customer is None:

                    self.send_json({
                        "success": False,
                        "message":
                        "No customer is currently being served."
                    })

                    return


                # Customer successfully completed

                self.send_json({
                    "success": True,
                    "token":
                    customer["token_id"]
                })


            except Exception as error:

                self.send_json(
                    {
                        "error": str(error)
                    },
                    500
                )


        # ================================================
        # UNKNOWN POST URL
        # ================================================

        else:

            self.send_json(
                {
                    "error": "API endpoint not found"
                },
                404
            )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    server_address = (
        "localhost",
        8000
    )

    server = HTTPServer(
        server_address,
        SmartQueueServer
    )

    print()
    print("======================================")
    print("     Smart Queue Backend Running")
    print("======================================")
    print()
    print("Server URL:")
    print("http://localhost:8000")
    print()
    print("Keep this terminal running.")
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Server stopped.")

        server.server_close()

