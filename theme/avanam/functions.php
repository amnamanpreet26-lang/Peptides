<?php
/**
 * Base functions and definitions
 *
 * This file must be parseable by PHP 5.2.
 *
 * @link https://developer.wordpress.org/themes/basics/theme-functions/
 *
 * @package Base
 */

define( 'AVANAM_VERSION', '1.5.7' );
define( 'AVANAM_MINIMUM_WP_VERSION', '6.0' );
define( 'AVANAM_MINIMUM_PHP_VERSION', '7.4' );

// Bail if requirements are not met.
if ( version_compare( $GLOBALS['wp_version'], AVANAM_MINIMUM_WP_VERSION, '<' ) || version_compare( phpversion(), AVANAM_MINIMUM_PHP_VERSION, '<' ) ) {
	require get_template_directory() . '/inc/back-compat.php';
	return;
}
// Include WordPress shims.
require get_template_directory() . '/inc/wordpress-shims.php';

// Load the `webapp()` entry point function.
require get_template_directory() . '/inc/class-theme.php';

// Load the `webapp()` entry point function.
require get_template_directory() . '/inc/functions.php';

// Initialize the theme.
call_user_func( 'Base\webapp' );

// Compound Index product archive layout.
require get_template_directory() . '/inc/compound-index/compound-index.php';




function allow_custom_font_uploads($mimes) {
    $mimes['woff']  = 'font/woff';
    $mimes['woff2'] = 'font/woff2';
    $mimes['ttf']   = 'font/ttf';
    $mimes['otf']   = 'font/otf';

    return $mimes;
}
add_filter('upload_mimes', 'allow_custom_font_uploads');



function load_satoshi_font() {
    ?>
    <style>
        @font-face {
            font-family: 'Satoshi';
            src: url('https://mediumturquoise-jay-726197.hostingersite.com/wp-content/uploads/2026/08/Satoshi-Light.woff2') format('woff2');
            font-weight: 300;
            font-style: normal;
            font-display: swap;
        }

        @font-face {
            font-family: 'Satoshi';
            src: url('https://mediumturquoise-jay-726197.hostingersite.com/wp-content/uploads/2026/08/Satoshi-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }

        @font-face {
            font-family: 'Satoshi';
            src: url('https://mediumturquoise-jay-726197.hostingersite.com/wp-content/uploads/2026/08/Satoshi-Medium.woff2') format('woff2');
            font-weight: 500;
            font-style: normal;
            font-display: swap;
        }
    </style>
    <?php
}
add_action('wp_head', 'load_satoshi_font');