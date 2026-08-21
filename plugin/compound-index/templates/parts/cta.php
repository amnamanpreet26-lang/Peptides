<?php
/**
 * Closing panel below the grid.
 *
 * Override in your theme at yourtheme/compound-index/parts/cta.php
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

if ( ! Compound_Index_Settings::on( 'cta_enabled' ) ) {
	return;
}

$ci_title = Compound_Index_Settings::get( 'cta_title' );
$ci_text  = Compound_Index_Settings::get( 'cta_text' );
$ci_label = Compound_Index_Settings::get( 'cta_button_label' );
$ci_url   = Compound_Index_Settings::get( 'cta_button_url' );

if ( ! $ci_url ) {
	$ci_url = wc_get_page_permalink( 'shop' );
}

if ( ! $ci_title && ! $ci_text && ! $ci_label ) {
	return;
}
?>
<aside class="ci-cta">
	<div class="ci-cta__copy">
		<?php if ( $ci_title ) : ?>
			<h2 class="ci-cta__title"><?php echo esc_html( $ci_title ); ?></h2>
		<?php endif; ?>
		<?php if ( $ci_text ) : ?>
			<p class="ci-cta__text"><?php echo wp_kses_post( $ci_text ); ?></p>
		<?php endif; ?>
	</div>

	<?php if ( $ci_label && $ci_url ) : ?>
		<a class="ci-btn" href="<?php echo esc_url( $ci_url ); ?>">
			<?php echo esc_html( $ci_label ); ?>
			<span class="ci-btn__arrow" aria-hidden="true">&rarr;</span>
		</a>
	<?php endif; ?>
</aside>
