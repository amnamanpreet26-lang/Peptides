<?php
/**
 * Search field, category chips, result count and sorting.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

$ci_chips = avanam_ci_chips();
$ci_count = avanam_ci_on( 'result_count' ) ? avanam_ci_result_count() : '';
$ci_sort  = avanam_ci_on( 'sorting' );
$ci_find  = avanam_ci_on( 'search' );
$ci_term  = avanam_ci_current_term();

if ( ! $ci_chips && ! $ci_count && ! $ci_sort && ! $ci_find ) {
	return;
}
?>
<div class="ci-toolbar">

	<div class="ci-toolbar__filters">

		<?php if ( $ci_find ) : ?>
			<form class="ci-search" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
				<label class="screen-reader-text" for="ci-search-field"><?php esc_html_e( 'Search products', 'avanam' ); ?></label>
				<svg class="ci-search__icon" viewBox="0 0 20 20" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false">
					<circle cx="9" cy="9" r="6"></circle><path d="m13.5 13.5 3.5 3.5"></path>
				</svg>
				<input id="ci-search-field" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Search products', 'avanam' ); ?>">
				<input type="hidden" name="post_type" value="product">
				<?php if ( $ci_term ) : ?>
					<input type="hidden" name="product_cat" value="<?php echo esc_attr( $ci_term->slug ); ?>">
				<?php endif; ?>
			</form>
		<?php endif; ?>

		<?php if ( $ci_chips ) : ?>
			<ul class="ci-chips">
				<?php foreach ( $ci_chips as $ci_chip ) : ?>
					<li>
						<a class="ci-chip<?php echo $ci_chip['active'] ? ' is-active' : ''; ?>" href="<?php echo esc_url( $ci_chip['url'] ); ?>" <?php echo $ci_chip['active'] ? 'aria-current="page"' : ''; ?>>
							<?php echo esc_html( $ci_chip['label'] ); ?>
							<?php if ( null !== $ci_chip['count'] && avanam_ci_on( 'chip_counts' ) ) : ?>
								<span class="ci-chip__count"><?php echo esc_html( number_format_i18n( $ci_chip['count'] ) ); ?></span>
							<?php endif; ?>
						</a>
					</li>
				<?php endforeach; ?>
			</ul>
		<?php endif; ?>

	</div>

	<?php if ( $ci_count || $ci_sort ) : ?>
		<div class="ci-toolbar__meta">
			<?php if ( $ci_count ) : ?>
				<p class="ci-resultcount"><?php echo esc_html( $ci_count ); ?></p>
			<?php endif; ?>

			<?php if ( $ci_sort ) : ?>
				<form class="ci-sort" method="get">
					<label for="ci-orderby"><?php esc_html_e( 'Sort', 'avanam' ); ?></label>
					<select id="ci-orderby" name="orderby" class="orderby" onchange="this.form.submit()">
						<?php
						// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- read-only sort preference.
						$ci_current = isset( $_GET['orderby'] ) ? wc_clean( wp_unslash( $_GET['orderby'] ) ) : get_option( 'woocommerce_default_catalog_orderby', 'menu_order' );
						foreach ( apply_filters( 'woocommerce_catalog_orderby', array() ) as $ci_key => $ci_label ) :
							?>
							<option value="<?php echo esc_attr( $ci_key ); ?>" <?php selected( $ci_current, $ci_key ); ?>><?php echo esc_html( $ci_label ); ?></option>
						<?php endforeach; ?>
					</select>
					<input type="hidden" name="paged" value="1">
					<?php wc_query_string_form_fields( null, array( 'orderby', 'submit', 'paged', 'product-page' ) ); ?>
				</form>
			<?php endif; ?>
		</div>
	<?php endif; ?>

</div>
