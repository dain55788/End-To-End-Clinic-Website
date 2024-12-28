const toTop = document.querySelector(".top");

window.addEventListener("scroll", () => {
    if(window.scrollY > 100)
        toTop.classList.add("active");
    else
        toTop.classList.remove("active");
})