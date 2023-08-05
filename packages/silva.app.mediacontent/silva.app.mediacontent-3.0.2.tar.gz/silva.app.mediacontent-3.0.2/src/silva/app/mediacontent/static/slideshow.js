
(function($) {

    var createSlideshow = function() {
        var $slides = $('.slideshow-slide', this);
        var $container = $('.slideshow-slides', this);
        var $left = $('.slideshow-left-control', this);
        var $right = $('.slideshow-right-control', this);
        var $markers = $('.slideshow-marker', this);
        var currentPosition = 0;
        var numberOfSlides = $slides.length;
        var slideWidth = $slides.width();


        // manageControls: Hides and shows controls depending on currentPosition
        function update(position) {
            // Hide left arrow if position is first slide
            if (position <= 0) {
                position = 0;
                $left.stop().fadeOut();
            }
            else {
                $left.stop().fadeIn();
            };
            // Hide right arrow if position is last slide
            if (position >= numberOfSlides - 1) {
                position = numberOfSlides - 1;
                $right.stop().fadeOut();
            }
            else {
                $right.stop().fadeIn();
            };
            $markers.filter('.current').removeClass('current');
            $($markers.get(position)).addClass('current');
            $container.stop().animate({
                marginLeft: slideWidth * (-position)
            });
            currentPosition = position;
        }
        function handleControl(event) {
            var position = $(this).hasClass('slideshow-right-control') ?
                currentPosition + 1 :
                currentPosition - 1;
            update(position);
          event.preventDefault();
        };

        $left.bind('click', handleControl);
        $right.bind('click', handleControl);
    };

    $(document).ready(function(){
        $('.slideshow').each(createSlideshow);
    });

})(jQuery);
