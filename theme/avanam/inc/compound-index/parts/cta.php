<?php
/**
 * Closing panel below the grid.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

if ( ! avanam_ci_on( 'cta' ) ) {
	return;
}

$ci_title  = avanam_ci_option( 'cta_title' );
$ci_text   = avanam_ci_option( 'cta_text' );
$ci_button = avanam_ci_option( 'cta_button' );
$ci_url    = avanam_ci_option( 'cta_url' );

if ( ! $ci_url ) {
	$ci_url = wc_get_page_permalink( 'shop' );
}

if ( ! $ci_title && ! $ci_text && ! $ci_button ) {
	return;
}
?>
<aside class="ci-cta">
	<div class="ci-cta__copy">
		<?php if ( $ci_title ) : ?>
			<h2 class="ci-cta__title"><?php echo esc_html( avanam_ci_tokens( $ci_title ) ); ?></h2>
		<?php endif; ?>
		<?php if ( $ci_text ) : ?>
			<p class="ci-cta__text"><?php echo esc_html( avanam_ci_tokens( $ci_text ) ); ?></p>
		<?php endif; ?>
	</div>

	<?php if ( $ci_button && $ci_url ) : ?>
		<a class="ci-btn" href="<?php echo esc_url( $ci_url ); ?>">
			<?php echo esc_html( $ci_button ); ?>
			<span class="ci-btn__arrow" aria-hidden="true">&rarr;</span>
		</a>
	<?php endif; ?>
</aside>
