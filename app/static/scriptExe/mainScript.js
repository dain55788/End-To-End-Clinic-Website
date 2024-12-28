const toTop = document.querySelector(".top");
let imgBtn = document.querySelectorAll('.img-btn')
//   navbar function 
$(document).ready(function(){

    $('.fa-bars').click(function(){
        $(this).toggleClass('fa-times');
        $('.navbar').toggleClass('nav-toggle');
    });

    $(window).on('scroll load',function(){
        $('.fa-bars').removeClass('fa-times');
        $('.navbar').removeClass('nav-toggle');

        if($(Window).scrollTop()  >  30){
            $('header').addClass('header-active');
        }else{
            $('header').removeClass('header-active');
        }
    });

    
});

// Image sliding event:
imgBtn.forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelector('.controls .active').classList.remove('active');
        btn.classList.add('active');
        let src = btn.getAttribute('data-src');
        document.querySelector('#image-slider').src = src;
    });
});

// Review section:
var swiper = new Swiper(".review-slider", {
    spaceBetween : 20,
    loop : true,
    autoplay : {
        delay : 3000,
        disableOnInteraction : false,
    },
    breakpoints: {
        640: {
            slidesPerView : 1,
        },
        768: {
            slidesPerView : 2,
        },
        1024: {
            slidesPerView : 3,
        },
    },
});

// GO TO TOP BUTTON
window.addEventListener("scroll", () => {
    if(window.scrollY > 100)
        toTop.classList.add("active");
    else
        toTop.classList.remove("active");
})


// Review section
var swiper = new Swiper(".review-slider", {
    spaceBetween : 20,
    loop : true,
    autoplay : {
        delay : 3000,
        disableOnInteraction : false,
    },
    breakpoints: {
        640: {
            slidesPerView : 1,
        },
        768: {
            slidesPerView : 2,
        },
        1024: {
            slidesPerView : 3,
        },
    },
});