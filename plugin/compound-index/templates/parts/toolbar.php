<?php
/**
 * Search box, category chips, result count and sorting.
 *
 * Override in your theme at yourtheme/compound-index/parts/toolbar.php
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

$ci_chips = Compound_Index_Template::chips();
$ci_count = Compound_Index_Settings::on( 'count_enabled' ) ? Compound_Index_Template::result_count() : '';
$ci_sort  = Compound_Index_Settings::on( 'sort_enabled' );
$ci_find  = Compound_Index_Settings::on( 'search_enabled' );

if ( ! $ci_chips && ! $ci_count && ! $ci_sort && ! $ci_find ) {
	return;
}
?>
<div class="ci-toolbar">

	<div class="ci-toolbar__filters">

		<?php if ( $ci_find ) : ?>
			<form class="ci-search" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
				<label class="screen-reader-text" for="ci-search-field"><?php esc_html_e( 'Search products', 'compound-index' ); ?></label>
				<svg class="ci-search__icon" viewBox="0 0 20 20" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false">
					<circle cx="9" cy="9" r="6"></circle><path d="m13.5 13.5 3.5 3.5"></path>
				</svg>
				<input
					id="ci-search-field"
					type="search"
					name="s"
					value="<?php echo esc_attr( get_search_query() ); ?>"
					placeholder="<?php echo esc_attr( Compound_Index_Settings::get( 'search_placeholder' ) ); ?>">
				<?php Compound_Index_Template::search_hidden_fields(); ?>
			</form>
		<?php endif; ?>

		<?php if ( $ci_chips ) : ?>
			<ul class="ci-chips">
				<?php foreach ( $ci_chips as $ci_chip ) : ?>
					<li>
						<a
							class="ci-chip<?php echo $ci_chip['active'] ? ' is-active' : ''; ?>"
							href="<?php echo esc_url( $ci_chip['url'] ); ?>"
							<?php echo $ci_chip['active'] ? 'aria-current="page"' : ''; ?>>
							<?php echo esc_html( $ci_chip['label'] ); ?>
							<?php if ( null !== $ci_chip['count'] && Compound_Index_Settings::on( 'chips_show_count' ) ) : ?>
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
					<label for="ci-orderby"><?php esc_html_e( 'Sort', 'compound-index' ); ?></label>
					<select id="ci-orderby" name="orderby" class="orderby">
						<?php
						$ci_catalog = wc_get_loop_prop( 'is_search' ) ? 'relevance' : get_option( 'woocommerce_default_catalog_orderby', 'menu_order' );
						// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- read-only sort preference.
						$ci_current = isset( $_GET['orderby'] ) ? wc_clean( wp_unslash( $_GET['orderby'] ) ) : $ci_catalog;

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
