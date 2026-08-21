<?php
/**
 * Product archive - Compound Index layout.
 *
 * Overrides wp-content/plugins/woocommerce/templates/archive-product.php.
 *
 * The loop is WooCommerce's ordinary main query, so category archives, search,
 * sorting and pagination behave exactly as they normally do and no product data
 * is invented here.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

get_header( 'shop' );

/** Opens the theme's content wrapper. */
do_action( 'woocommerce_before_main_content' );

$ci_columns = absint( avanam_ci_option( 'columns' ) );
$ci_columns = $ci_columns ? $ci_columns : 3;
?>

<div class="compound-index">

	<?php avanam_ci_part( 'header' ); ?>

	<?php avanam_ci_part( 'toolbar' ); ?>

	<?php
	/** Store notices, and anything plugins add above the loop. */
	do_action( 'woocommerce_before_shop_loop' );
	?>

	<?php if ( have_posts() ) : ?>

		<div class="ci-grid ci-grid--<?php echo esc_attr( $ci_columns ); ?>">
			<?php
			while ( have_posts() ) :
				the_post();
				avanam_ci_part( 'card' );
			endwhile;
			?>
		</div>

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
