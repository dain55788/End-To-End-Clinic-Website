document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.querySelector("input[type='date']");
    const today = new Date();
    dateInput.value = today.toISOString().split("T")[0];
});

let counter = 1; // Biến đếm bắt đầu từ 1
function themThuoc() {

    const newMedItem = document.createElement("div");
    newMedItem.className = `row med-item pb-sm-2`;

    // Nội dung bên trong div mới
    newMedItem.innerHTML = `
            <div class="col-sm-3 text-center">
                  <input type="text" name="medicine${counter}" list="medicineList">
                  <datalist id="medicineList">
                    {% for t in thuocs %}
                        <option value="{{ t.TenThuoc }}">
                    {% endfor %}
                  </datalist>
            </div>
            <div class="col-sm-7 text-center">
                <input type="text" id="med-instruct${counter}" name="med-instruct${counter}" class="border med-instruct${counter}" placeholder="Cách dùng">
            </div>
            <div class="col-sm-2 text-center">
                <input type="text" id="med-number${counter}" name="med-number${counter}" class="border med-number${counter}" placeholder="Số lượng">
            </div>
      `;

    // Thêm div mới vào container
    document.getElementById("med-container").appendChild(newMedItem);

    // Tăng giá trị của counter để các lớp lần sau được cập nhật
    counter++;
}

function xoaThuoc() {
    const medItems = document.querySelectorAll("#med-container .med-item");
    // Kiểm tra nếu có hơn một phần tử
    if (medItems.length > 1) {
        const lastMedItem = medItems[medItems.length - 1];
        lastMedItem.remove();
    }
}