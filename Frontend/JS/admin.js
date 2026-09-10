
// =========================================================
// LOAD ADMIN DATA
// =========================================================

async function loadAdminData() {

    try {

        const response = await fetch(
            "http://localhost:8000/api/admin"
        );

        const data = await response.json();


        // -------------------------------------------------
        // UPDATE STATISTICS
        // -------------------------------------------------

        document.getElementById(
            "waitingCount"
        ).textContent =
            data.statistics.waiting;


        document.getElementById(
            "completedCount"
        ).textContent =
            data.statistics.completed;


        // -------------------------------------------------
        // UPDATE QUEUE TABLE
        // -------------------------------------------------

        const table =
            document.getElementById(
                "queueTable"
            );

        table.innerHTML = "";


        data.customers.forEach(
            function(customer) {

                const row =
                    document.createElement("tr");


                // Priority text

                const priority =
                    customer.priority == 1
                        ? "Priority"
                        : "Normal";


                row.innerHTML = `

                    <td>
                        A${String(
                            customer.token_id
                        ).padStart(3, "0")}
                    </td>

                    <td>
                        ${customer.customer_name}
                    </td>

                    <td>
                        ${customer.service}
                    </td>

                    <td>
                        ${priority}
                    </td>

                    <td>
                        ${customer.status}
                    </td>

                `;


                table.appendChild(row);

            }
        );


    } catch (error) {

        console.error(
            "Unable to load admin data:",
            error
        );

    }

}


// =========================================================
// SERVE NEXT CUSTOMER
// =========================================================

document.getElementById(
    "serveButton"
).addEventListener(
    "click",
    async function() {

        try {

            const response =
                await fetch(
                    "http://localhost:8000/api/serve",
                    {
                        method: "POST"
                    }
                );


            const result =
                await response.json();


            console.log(
                "Serve API response:",
                result
            );


            if (result.success) {

                alert(
                    "Now serving token A" +
                    String(
                        result.token
                    ).padStart(3, "0")
                );


                // Refresh admin data

                loadAdminData();

            } else {

                alert(
                    result.message
                );

            }


        } catch (error) {

            console.error(
                error
            );

            alert(
                "Unable to connect to server."
            );

        }

    }
);


// =========================================================
// COMPLETE CURRENT CUSTOMER
// =========================================================

document.getElementById(
    "completeButton"
).addEventListener(
    "click",
    async function() {

        try {

            const response =
                await fetch(
                    "http://localhost:8000/api/complete",
                    {
                        method: "POST"
                    }
                );


            const result =
                await response.json();


            console.log(
                "Complete API response:",
                result
            );


            if (result.success) {

                alert(
                    "Token A" +
                    String(
                        result.token
                    ).padStart(3, "0") +
                    " completed successfully."
                );


                // Refresh admin data

                loadAdminData();

            } else {

                alert(
                    result.message
                );

            }


        } catch (error) {

            console.error(
                error
            );

            alert(
                "Unable to connect to server."
            );

        }

    }
);


// =========================================================
// INITIAL LOAD
// =========================================================

loadAdminData();


// =========================================================
// AUTO REFRESH EVERY 5 SECONDS
// =========================================================

setInterval(
    loadAdminData,
    5000
);

