// Synchronize the date
document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("date"); // Get the date input
    const readonlyInput = document.querySelector(".list-section h3 input[type='text']"); // Get the readonly input

    // Listen for changes on the date input
    dateInput.addEventListener("change", function () {
        if (dateInput.value) {
            // Update readonly input with the selected date
            readonlyInput.value = dateInput.value;
        }
    });
});

// execute the button lap danh sach
//document.addEventListener("DOMContentLoaded", function () {
//    const generateBtn = document.querySelector(".final-btn");
//
//    if (generateBtn) {
//        generateBtn.addEventListener("click", function (event) {
//            event.preventDefault(); // Prevent default behavior
//
//            // Retrieve data from the server-side variable
//            const matchedArrangements = {{ matched_arrangements | tojson | safe }};
//
//            if (matchedArrangements.length > 0) {
//                fetch("/save_arrangements", {
//                    method: "POST",
//                    headers: {
//                        "Content-Type": "application/json", // Explicitly set Content-Type
//                    },
//                    body: JSON.stringify({ matched_arrangements: matchedArrangements }), // Send JSON data
//                })
//                    .then(response => {
//                        if (!response.ok) {
//                            throw new Error(`HTTP error! status: ${response.status}`);
//                        }
//                        return response.json();
//                    })
//                    .then(data => {
//                        alert(data.message); // Show success or error message
//                    })
//                    .catch(error => {
//                        console.error("Fetch error:", error);
//                        alert("An error occurred while saving.");
//                    });
//            } else {
//                alert("No data to save.");
//            }
//        });
//    }
//});

document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.querySelector('.final-btn');
    const pdfForm = document.getElementById('pdfForm');

    generateBtn.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default form submission

        fetch('/save_arrangements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                pdfForm.style.display = 'block';
            } else {
                alert(data.message); // Show error message
            }
        })
        .catch(error => {
            alert('Đã xảy ra lỗi khi lưu danh sách!');
            console.error('Error:', error);
        });
    });
});


