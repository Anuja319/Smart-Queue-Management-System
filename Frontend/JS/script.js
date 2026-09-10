const form = document.getElementById("tokenForm");

form.addEventListener("submit", async function(event) {

    event.preventDefault();


    const customerName =
        document.getElementById(
            "customerName"
        ).value;


    const service =
        document.getElementById(
            "service"
        ).value;


    const priority =
        document.getElementById(
            "priority"
        ).value;


    const data = {

        customer_name: customerName,

        service: service,

        priority: priority

    };


    try {

        const response = await fetch(
            "http://localhost:8000/api/generate",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        const result =
            await response.json();


        if (result.success) {

            document.getElementById(
                "tokenResult"
            ).classList.remove(
                "hidden"
            );


            document.getElementById(
                "tokenNumber"
            ).textContent =
                result.token;


            form.reset();

        } else {

            alert(result.error);

        }

    } catch (error) {

        alert(
            "Unable to connect to server."
        );

        console.error(error);

    }

});