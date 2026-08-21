<?php
/**
 * Product archive - Compound Index layout.
 *
 * Overrides wp-content/plugins/woocommerce/templates/archive-product.php.
 *
 * The header and toolbar are ours; the product grid below is WooCommerce's
 * ordinary loop, rendered by the theme, so product cards keep every class the
 * theme and its stylesheet expect.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

get_header( 'shop' );

/** Opens the theme's content wrapper. */
do_action( 'woocommerce_before_main_content' );
?>

<div class="compound-index">

	<?php avanam_ci_part( 'header' ); ?>

	<?php avanam_ci_part( 'toolbar' ); ?>

	<?php
	/** Store notices, and anything plugins add above the loop. */
	do_action( 'woocommerce_before_shop_loop' );
	?>

	<?php if ( woocommerce_product_loop() ) : ?>

		<?php woocommerce_product_loop_start(); ?>

			<?php
			while ( have_posts() ) :
				the_post();

				/** Lets plugins hook each item, as they would on any archive. */
				do_action( 'woocommerce_shop_loop' );

				wc_get_template_part( 'content', 'product' );
			endwhile;
			?>

		<?php woocommerce_product_loop_end(); ?>

		<?php avanam_ci_part( 'pagination' ); ?>

	<?php else : ?>

		<?php avanam_ci_part( 'empty' ); ?>

	<?php endif; ?>

	<?php do_action( 'woocommerce_after_shop_loop' ); ?>

	<?php avanam_ci_part( 'cta' ); ?>

</div>

<?php
do_action( 'woocommerce_after_main_content' );

get_footer( 'shop' );
