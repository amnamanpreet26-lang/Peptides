<?php
/**
 * The Compound Index product archive.
 *
 * Override in your theme by copying this file to
 * yourtheme/compound-index/archive-product.php
 *
 * The loop below is WooCommerce's ordinary main query, so category archives,
 * search, sorting and pagination all keep working exactly as they do normally.
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

get_header( 'shop' );

/**
 * Opens the theme's content wrapper. Kept so the archive still sits inside
 * whatever markup the active theme expects.
 */
do_action( 'woocommerce_before_main_content' );

$ci_columns = absint( Compound_Index_Settings::get( 'columns', 3 ) );
?>

<div class="compound-index">

	<?php compound_index_part( 'parts/page-header' ); ?>

	<?php compound_index_part( 'parts/toolbar' ); ?>

	<?php
	/** Store notices and anything third-party plugins add above the loop. */
	do_action( 'woocommerce_before_shop_loop' );
	?>

	<?php if ( have_posts() ) : ?>

		<div class="ci-grid ci-grid--<?php echo esc_attr( $ci_columns ); ?>">
			<?php
			while ( have_posts() ) :
				the_post();
				compound_index_part( 'content-product' );
			endwhile;
			?>
		</div>

		<?php compound_index_part( 'parts/pagination' ); ?>

	<?php else : ?>

		<?php compound_index_part( 'parts/empty' ); ?>

	<?php endif; ?>

	<?php do_action( 'woocommerce_after_shop_loop' ); ?>

	<?php compound_index_part( 'parts/cta' ); ?>

</div>

<?php
do_action( 'woocommerce_after_main_content' );

get_footer( 'shop' );
