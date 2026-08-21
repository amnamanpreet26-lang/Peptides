<?php
/**
 * One compound card in the archive grid.
 *
 * Override in your theme by copying this file to
 * yourtheme/compound-index/content-product.php
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

global $product;

if ( ! $product instanceof WC_Product ) {
	$product = wc_get_product( get_the_ID() );
}

if ( ! $product || ! $product->is_visible() ) {
	return;
}

$ci_badges = Compound_Index_Template::badges( $product );
$ci_spec   = Compound_Index_Product_Meta::spec_line( $product );
$ci_rows   = Compound_Index_Product_Meta::data_rows( $product );
$ci_link   = get_permalink( $product->get_id() );
$ci_image  = $product->get_image( 'woocommerce_thumbnail', array( 'class' => 'ci-card__img', 'loading' => 'lazy' ) );
?>
<article class="ci-card" data-product-id="<?php echo esc_attr( $product->get_id() ); ?>">

	<a class="ci-card__media" href="<?php echo esc_url( $ci_link ); ?>" tabindex="-1" aria-hidden="true">
		<?php
		echo $ci_image ? wp_kses_post( $ci_image ) : wp_kses_post( wc_placeholder_img( 'woocommerce_thumbnail', array( 'class' => 'ci-card__img' ) ) );
		?>

		<?php if ( $ci_badges ) : ?>
			<span class="ci-card__badges">
				<?php foreach ( $ci_badges as $ci_badge ) : ?>
					<span class="ci-badge ci-badge--<?php echo esc_attr( $ci_badge['tone'] ); ?>"><?php echo esc_html( $ci_badge['label'] ); ?></span>
				<?php endforeach; ?>
			</span>
		<?php endif; ?>
	</a>

	<div class="ci-card__body">

		<h2 class="ci-card__title">
			<a href="<?php echo esc_url( $ci_link ); ?>"><?php echo esc_html( $product->get_name() ); ?></a>
		</h2>

		<?php if ( $ci_spec ) : ?>
			<p class="ci-card__spec"><?php echo esc_html( $ci_spec ); ?></p>
		<?php endif; ?>

		<?php if ( $ci_rows ) : ?>
			<dl class="ci-card__data">
				<?php foreach ( $ci_rows as $ci_label => $ci_value ) : ?>
					<div class="ci-card__row">
						<dt><?php echo esc_html( $ci_label ); ?></dt>
						<dd><?php echo esc_html( $ci_value ); ?></dd>
					</div>
				<?php endforeach; ?>
			</dl>
		<?php endif; ?>

		<a class="ci-card__link" href="<?php echo esc_url( $ci_link ); ?>">
			<?php esc_html_e( 'Specification', 'compound-index' ); ?>
			<span class="screen-reader-text"><?php echo esc_html( $product->get_name() ); ?></span>
			<span class="ci-card__arrow" aria-hidden="true">&rarr;</span>
		</a>

		<?php
		/**
		 * Room for an Add to Cart button, wishlist icon or anything else that
		 * would normally hook woocommerce_after_shop_loop_item.
		 *
		 * @param WC_Product $product Product being rendered.
		 */
		do_action( 'compound_index_after_card_body', $product );
		?>

	</div>

</article>
