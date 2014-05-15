// Populate the variables
var fullWidth       = $( window ).width(),
    contWidth       = $( ".container" ).width(),
    fullPad         = Math.floor( ( fullWidth - contWidth ) / 2 ),
    dataWidth       = $( ".post-header" ).data( "width" ),
    dataHeight      = $( ".post-header" ).data( "height" ),
    currentWidth    = $( ".post-header" ).width(),
    currentHeight   = $( ".post-header" ).height(),
    titleHeight     = $( ".post-title" ).outerHeight(),
    headerHeight    = $( "#header" ).outerHeight(),
    newHeight       = Math.ceil( currentWidth * dataHeight / dataWidth );


// Re-populate the variables
function varRefresh() {
    fullWidth       = $( window ).width();
    contWidth       = $( ".container" ).width();
    fullPad         = Math.floor( ( fullWidth - contWidth ) / 2 );
    dataWidth       = $( ".post-header" ).data( "width" );
    dataHeight      = $( ".post-header" ).data( "height" );
    currentWidth    = $( ".post-header" ).width();
    currentHeight   = $( ".post-header" ).height();
    titleHeight     = $( ".post-title" ).outerHeight();
    newHeight       = Math.ceil( currentWidth * dataHeight / dataWidth );
}

// Show menu if not on mobile
function showMenu() {
    if ( fullWidth >= 768 ) {
        $( "#nav-top" ).addClass( "in" );
    } else {
        $( "#nav-top" ).removeClass( "in" );
    }
}

showMenu();


// Make .full full width using padding and negative margins
function makeFull() {
    $( ".full" ).css({
        width:          fullWidth,
        marginLeft:     -fullPad
    });
    $( ".full-pad" ).css({
        paddingLeft:    fullPad,
        paddingRight:   fullPad,
        marginLeft:     -fullPad,
        marginRight:    -fullPad
    });
    $( ".full .full-pad" ).css({
        width:          fullWidth,
        marginLeft:     0,
        marginRight:    0
    });
}

makeFull();


// Set video background in .jumbotron to full size
function jumboVideo() {
    var jumboHeight = $( ".jumbotron" ).height() + 180,
        jumboWidth  = $( ".jumbotron" ).width() + 30;

    $( ".video-box" ).height( jumboHeight ).width( jumboWidth );
}

jumboVideo();


// Make jCarousel slides the width of the container
function slideSize() {
    $( ".jcarousel-slide" ).width( contWidth - 60 );
}

slideSize();


// Bind events to window resize
$( window ).resize(function() {
    varRefresh();
    makeFull();
    jumboVideo();
    showMenu();
    slideSize();
});


// Blog effects

// Blur the image on scroll down, Medium style
$( window ).scroll(function() {
    var s           = $( window ).scrollTop(),
        opacityVal  = ( s / ( currentHeight / 2 ) );

    $( ".ph-blurred" ).css( "opacity", opacityVal );
});


// Expand the image on tap
$( ".ph-bg" ).click(function() {
    if( $( ".post-header" ).hasClass( "closed" ) ) {
        $( ".post-header" ).animate({
            height:         newHeight,
            marginBottom:   titleHeight + 30
        }, 400 ).toggleClass( "closed" );
        $( ".post-title" ).animate({
            opacity:        0,
            bottom:         -titleHeight
        }, 200 ).animate({ opacity: 1 }, 500 );
    } else {
        $( ".post-header" ).animate({
            height:         400,
            marginBottom:   30
        }, 200 ).toggleClass( "closed" );
        $( ".post-title" ).css({
            opacity:        0,
            bottom:         0
        }).animate({ opacity: 1 }, 500 );
    }
});


// Setup jCarousel
if ( $( ".jcarousel" ).length ) {
    $(function() {
        $( ".jcarousel" ).jcarousel({
            list:   ".jcarousel-tray",
            items:  ".jcarousel-slide",
            wrap:   "circular",
            center: true
        }).jcarouselAutoscroll({
            interval: 10000,
            create: $( ".jcarousel" ).hover(function() {
                $( this ).jcarouselAutoscroll( "stop" );
            }, function() {
                $( this ).jcarouselAutoscroll( "start" );
            })
        });

        $( ".jcarousel-prev" ).jcarouselControl({
            target: "-=1"
        });

        $( ".jcarousel-next" ).jcarouselControl({
            target: "+=1"
        });
    });
}

// Vote button functionality
$( ".btn-vote" ).click(function(e) {
    if ( !$( this ).hasClass( "voted" ) ) {
        e.preventDefault();
        var vote = $( this ).data( "vote" ),
            type = $( this ).data( "vote-type" );
        $( this ).addClass( "voted" );
        console.log( "VOTED! " + vote + ": " + type );
    }
});


