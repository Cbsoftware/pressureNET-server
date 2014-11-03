// Populate the variables
var fullWidth       = $( window ).width(),
    contWidth       = $( ".container" ).width(),
    fullMar         = Math.floor( ( fullWidth - contWidth ) / 2 ),
    fullPad         = Math.floor( ( fullWidth - ( contWidth + 30 ) ) / 2 -1 ),
    headerHeight    = $( "#header" ).outerHeight(),
    titleHeight     = $( ".post-title" ).innerHeight(),
    fullHeight      = $( window ).height() - headerHeight,
    phFullWidth     = $( ".post-header" ).data( "width" ),
    phFullHeight    = $( ".post-header" ).data( "height" ),
    phCurrentHeight = $( ".post-header" ).height(),
    phMaxHeight     = ( phFullHeight > fullHeight ) ? fullHeight : phFullHeight;

// Re-populate the variables
function varRefresh() {
    fullWidth       = $( window ).width();
    contWidth       = $( ".container" ).width();
    fullMar         = Math.floor( ( fullWidth - contWidth ) / 2 );
    fullPad         = Math.floor( ( fullWidth - ( contWidth + 30 ) ) / 2 -1 );
    headerHeight    = $( "#header" ).outerHeight();
    fullHeight      = $( window ).height() - headerHeight;
    titleHeight     = $( ".post-title" ).innerHeight();
    phFullWidth     = $( ".post-header" ).data( "width" );
    phFullHeight    = $( ".post-header" ).data( "height" );
    phCurrentHeight = $( ".post-header" ).height();
    phMaxHeight     = ( phFullHeight > fullHeight ) ? fullHeight : phFullHeight;
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
    $( ".full:not(.post-header)" ).css({
        width:      fullWidth,
        marginLeft: -fullPad
    });
    $( ".full.post-header" ).css({
        width:      fullWidth,
        marginLeft: -fullMar
    });
    $( ".full-pad" ).css({
        paddingLeft:  fullPad,
        paddingRight: fullPad,
        marginLeft:   -fullPad,
        marginRight:  -fullPad
    });
    $( ".full .full-pad" ).css({
        width:       fullWidth,
        marginLeft:  0,
        marginRight: 0
    });
}

makeFull();


// Set video background in .jumbotron to full size
function jumboVideo() {
    var jumboHeight = $( ".jumbotron" ).height() + 263,
        jumboWidth  = $( ".jumbotron" ).width() + 30;

    $( ".video-box" ).height( jumboHeight ).width( jumboWidth );
}

jumboVideo();


// Make jCarousel slides the width of the container
function slideSize() {
    $( ".jcarousel" ).width( contWidth + 30 );
    $( ".jcarousel-slide" ).width( contWidth - 60 );
}

slideSize();


// Bind events to window resize
$( window ).resize(function() {
    varRefresh();
    makeFull();
    jumboVideo();
    showMenu();
    if ( $( ".jcarousel" ).length ) slideSize();
});


// Collapse panels
$( ".collapse-group" ).on( "show.bs.collapse", function () {
    $( this ).find( ".in" ).collapse( "hide" );
});


// Level-height leveling
$( ".level-group" ).each(function() {
    var maxHeight = 0;

    $( ".level-item" ).each(function() {
        maxHeight = maxHeight > $( this ).innerHeight() ? maxHeight : $( this ).innerHeight();
    });

    $( ".level-item" ).height( maxHeight );
});


// Blog effects

// Scroll-based effects
$( window ).scroll(function() {
    var scroll     = $( window ).scrollTop(),
        opacityVal = ( scroll / ( phCurrentHeight / 2 ) );

// Blur the image on scroll down, Medium style
    $( ".ph-blurred" ).css( "opacity", opacityVal );

// #Header colourer
    if ( scroll > 90 ) {
        $( ".home #header" ).addClass( "scrolled" );
    } else {
        $( ".home #header" ).removeClass( "scrolled" );
    }
});

// Expand the image on tap
$( ".ph-bg" ).click(function() {
    if( $( ".post-header" ).hasClass( "closed" ) ) {
        $( ".post-header" ).animate({
            height:         phMaxHeight,
            marginBottom:   titleHeight + 30
        }, 400 ).toggleClass( "closed" );
        $( ".ph-bg" ).css( "background-size", "contain" );
        $( ".post-title" ).animate({
            opacity: 0,
            bottom:  -titleHeight
        }, 200 ).animate({ opacity: 1 }, 500 );
    } else {
        $( ".post-header" ).animate({
            height:         400,
            backgroundSize: "cover",
            marginBottom:   30
        }, 200 ).toggleClass( "closed" );
        $( ".ph-bg" ).css( "background-size", "cover" );
        $( ".post-title" ).css({
            opacity: 0,
            bottom:  0
        }).animate({ opacity: 1 }, 500 );
    }
});


// Sharing buttons

$( "#share-twitter" ).click(function(e) {
    var $this = $( this ),
        url = encodeURI( $this.data( "url" )),
        text = encodeURI( $this.data( "text" )),
        hashtags = $this.data( "hashtags" );

    e.preventDefault();

    window.open(
        this.href + "?url=" + url + "&text=" + text + "&hashtags=" + hashtags,
        "tweetDialog",
        "height=260, width=550, toolbar=0, status=0"
    );
});

$( "#share-facebook" ).click(function(e) {
    var $this = $( this ),
        href = encodeURI( $this.data( "href" )),
        redir = encodeURI( $this.data( "redir" )),
        appID = "711837532201345";

    e.preventDefault();

    window.open(
        this.href + "?u=" + href + "&app_id=" + appID,
        "facebookDialog",
        "height=600, width=600, toolbar=0, status=0"
    );
});

$( "#share-googleplus" ).on( "click", function(e) {
    var $this = $( this ),
        url = encodeURI( $this.data( "url" ));

    e.preventDefault();

    window.open(
        this.href + "?url=" + url,
        "gplusDialog",
        "height=600, width=600, toolbar=0, status=0"
    );
});

$( "#share-tumblr" ).on( "click", function(e) {
    var $this = $( this ),
        url = encodeURI( $this.data( "url" )),
        name = encodeURI( $this.data( "name" )),
        description = encodeURI( $this.data( "description" ));

    e.preventDefault();

    window.open(
        this.href + "?url=" + url + "&name=" + name + "&description=" + description,
        "tumblrDialog",
        "height=500, width=800, toolbar=0, status=0"
    );
});


$( "#share-reddit" ).on( "click", function(e) {
    var $this = $( this ),
        url = encodeURI( $this.data( "url" ));

    e.preventDefault();

    window.open(
        this.href + "?url=" + url,
        "redditDialog",
        "height=750, width=850, toolbar=0, status=0"
    );
});


$( "#share-stumbleupon" ).on( "click", function(e) {
    var $this = $( this ),
        url = encodeURI( $this.data( "url" ));

    e.preventDefault();

    window.open(
        this.href + "?url=" + url,
        "stumbleuponDialog",
        "height=525, width=800, toolbar=0, status=0"
    );
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
    if ( !$( this ).hasClass( "btn-email" ) ) e.preventDefault();

    if ( !$( this ).hasClass( "voted" ) ) {

        var vote = $( this ).data( "vote" ),
            type = $( this ).data( "vote-type" );

        $( this ).addClass( "voted" ).append( ' <i class="fa fa-check"></i>' )
        .before( '<div class="thanks">Thanks for voting!</div>' );
        $( ".thanks" ).delay( 3000 ).fadeOut( 500 );
    }
});

// Tab-group
if ( $( '#type-public[value="1"]' ).prop( "checked" ) || $( '#type-public[value="2"]' ).prop( "checked" ) ) {
    $( "#tab-link-sdk" ).removeClass( "active" );
    $( "#tab-link-api" ).addClass( "active" );
    $( "#signup-description" ).text( "This form is for signing up as a Researcher to pull raw pressure data from our servers." );
} else if ( $( '#type-public[value="3"]' ).prop( "checked" ) ) {
    $( "#tab-link-api" ).removeClass( "active" );
    $( "#tab-link-sdk" ).addClass( "active" );
    $( "#signup-description" ).text( "This form is for applying to the PressureNet Developer Program to integrate our SDK into your app." );
}

$( ".tab-link" ).click(function(e) {
    e.preventDefault();

    var tab = $( this ).data( "tab" );

    $( ".tab-link" ).removeClass( "active" );
    $( this ).addClass( "active" );

    if ( tab == "sdk" ) {
        $( "#signup-form").delay( 500 ).removeClass( "tab-api" ).addClass( "tab-sdk" );
        $( "#type-developer" ).val( "developer" );
        $( '#type-public[value="1"], #type-public[value="2"]' ).prop( "checked", false );
        $( '#type-public[value="3"]' ).prop( "checked", true );
        $( "#signup-description" ).text( "This form is for signing up as a Researcher to pull raw pressure data from our servers." );
    } else {
        $( "#signup-form").removeClass( "tab-sdk" ).addClass( "tab-api" );
        $( '#type-public[value="3"]' ).prop( "checked", false );
        $( "#signup-description" ).text( "This form is for applying to the PressureNet Developer Program to integrate our SDK into your app." );
    }
});
