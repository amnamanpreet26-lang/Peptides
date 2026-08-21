<?php
/**
 * Shop-page defaults for the Compound Index header.
 *
 * Product categories carry their own header fields; this screen covers the main
 * shop page and provides the fallback any category leaves blank.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

const AVANAM_CI_OPTION = 'avanam_compound_index';

/**
 * Defaults, matching the reference design.
 *
 * @return array
 */
function avanam_ci_defaults() {
	return array(
		'eyebrow'      => '',
		'title'        => __( 'Compound index', 'avanam' ),
		'intro'        => __( 'Every compound we produce, with its current specification and the lot most recently released. Open any entry for the full data sheet, certificate of analysis and handling notes.', 'avanam' ),
		'stat_1_value' => '{count}',
		'stat_1_label' => __( 'Compounds listed', 'avanam' ),
		'stat_2_value' => '',
		'stat_2_label' => __( 'Median purity', 'avanam' ),
		'stat_3_value' => '',
		'stat_3_label' => __( 'Lots with a COA', 'avanam' ),
		'stat_4_value' => '',
		'stat_4_label' => __( 'Records retained', 'avanam' ),
		'chips'        => 'yes',
		'chip_counts'  => 'yes',
		'chips_label'  => __( 'All', 'avanam' ),
		'search'       => 'yes',
		'result_count' => 'yes',
		'sorting'      => 'yes',
		'columns'      => '3',
		'spec_attrs'   => array(),
		'row_attrs'    => array(),
		'link_label'   => __( 'Specification', 'avanam' ),
		'badge'        => __( 'Documented', 'avanam' ),
		'cta'          => 'yes',
		'cta_title'    => __( 'Looking for something not listed?', 'avanam' ),
		'cta_text'     => __( 'The full index runs to every compound we hold, each with its own specification and certificate.', 'avanam' ),
		'cta_button'   => __( 'Browse all products', 'avanam' ),
		'cta_url'      => '',
	);
}

/**
 * Read a setting.
 *
 * @param string $key Setting key.
 * @return mixed
 */
function avanam_ci_option( $key ) {
	static $cache = null;

	if ( null === $cache ) {
		$saved = get_option( AVANAM_CI_OPTION, array() );
		$cache = wp_parse_args( is_array( $saved ) ? $saved : array(), avanam_ci_defaults() );
	}

	return array_key_exists( $key, $cache ) ? $cache[ $key ] : '';
}

/**
 * Convenience boolean read.
 *
 * @param string $key Setting key.
 * @return bool
 */
function avanam_ci_on( $key ) {
	return 'yes' === avanam_ci_option( $key );
}

/**
 * Global product attributes, for the card field pickers.
 *
 * @return array taxonomy => label
 */
function avanam_ci_attribute_choices() {
	$out = array();

	if ( ! function_exists( 'wc_get_attribute_taxonomies' ) ) {
		return $out;
	}

	foreach ( wc_get_attribute_taxonomies() as $attribute ) {
		$taxonomy         = wc_attribute_taxonomy_name( $attribute->attribute_name );
		$out[ $taxonomy ] = $attribute->attribute_label ? $attribute->attribute_label : $attribute->attribute_name;
	}

	return $out;
}

/**
 * Register the settings screen.
 */
function avanam_ci_admin_menu() {
	add_submenu_page(
		'edit.php?post_type=product',
		__( 'Compound Index', 'avanam' ),
		__( 'Compound Index', 'avanam' ),
		'manage_woocommerce',
		'avanam-compound-index',
		'avanam_ci_settings_page'
	);
}
add_action( 'admin_menu', 'avanam_ci_admin_menu' );

/**
 * Register the option and its sanitiser.
 */
function avanam_ci_register_setting() {
	register_setting(
		'avanam_compound_index',
		AVANAM_CI_OPTION,
		array(
			'type'              => 'array',
			'sanitize_callback' => 'avanam_ci_sanitize',
			'default'           => avanam_ci_defaults(),
		)
	);
}
add_action( 'admin_init', 'avanam_ci_register_setting' );

/**
 * Sanitise submitted settings.
 *
 * @param mixed $input Raw input.
 * @return array
 */
function avanam_ci_sanitize( $input ) {
	$defaults = avanam_ci_defaults();
	$input    = is_array( $input ) ? $input : array();
	$out      = array();

	foreach ( array( 'chips', 'chip_counts', 'search', 'result_count', 'sorting', 'cta' ) as $key ) {
		$out[ $key ] = empty( $input[ $key ] ) ? 'no' : 'yes';
	}

	$text = array( 'eyebrow', 'title', 'chips_label', 'link_label', 'badge', 'cta_title', 'cta_button' );
	for ( $i = 1; $i <= AVANAM_CI_STAT_SLOTS; $i++ ) {
		$text[] = 'stat_' . $i . '_value';
		$text[] = 'stat_' . $i . '_label';
	}
	foreach ( $text as $key ) {
		$out[ $key ] = isset( $input[ $key ] ) ? sanitize_text_field( wp_unslash( $input[ $key ] ) ) : $defaults[ $key ];
	}

	$out['intro']      = isset( $input['intro'] ) ? sanitize_textarea_field( wp_unslash( $input['intro'] ) ) : $defaults['intro'];
	$out['cta_text']   = isset( $input['cta_text'] ) ? sanitize_textarea_field( wp_unslash( $input['cta_text'] ) ) : $defaults['cta_text'];
	$out['cta_url']    = isset( $input['cta_url'] ) ? esc_url_raw( wp_unslash( $input['cta_url'] ) ) : '';
	$out['columns']    = (string) max( 2, min( 4, absint( $input['columns'] ?? 3 ) ) );
	$out['spec_attrs'] = array_map( 'sanitize_key', (array) ( $input['spec_attrs'] ?? array() ) );
	$out['row_attrs']  = array_map( 'sanitize_key', (array) ( $input['row_attrs'] ?? array() ) );

	return $out;
}

/**
 * Render the settings screen.
 */
function avanam_ci_settings_page() {
	if ( ! current_user_can( 'manage_woocommerce' ) ) {
		return;
	}

	$name  = AVANAM_CI_OPTION;
	$attrs = avanam_ci_attribute_choices();
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Compound Index', 'avanam' ); ?></h1>
		<p class="description" style="max-width:60em">
			<?php esc_html_e( 'The shop page header, and the fallback for any category that leaves a field blank. Per-category values are set on Products - Categories.', 'avanam' ); ?>
		</p>

		<form method="post" action="options.php">
			<?php settings_fields( 'avanam_compound_index' ); ?>

			<h2 class="title"><?php esc_html_e( 'Shop page header', 'avanam' ); ?></h2>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="ci-eyebrow"><?php esc_html_e( 'Eyebrow', 'avanam' ); ?></label></th>
					<td><input id="ci-eyebrow" class="regular-text" type="text" name="<?php echo esc_attr( "{$name}[eyebrow]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'eyebrow' ) ); ?>"></td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-title"><?php esc_html_e( 'Title', 'avanam' ); ?></label></th>
					<td><input id="ci-title" class="regular-text" type="text" name="<?php echo esc_attr( "{$name}[title]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'title' ) ); ?>"></td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-intro"><?php esc_html_e( 'Intro', 'avanam' ); ?></label></th>
					<td><textarea id="ci-intro" class="large-text" rows="3" name="<?php echo esc_attr( "{$name}[intro]" ); ?>"><?php echo esc_textarea( avanam_ci_option( 'intro' ) ); ?></textarea></td>
				</tr>
			</table>

			<h2 class="title"><?php esc_html_e( 'Counters', 'avanam' ); ?></h2>
			<p class="description" style="max-width:60em">
				<?php
				printf(
					/* translators: %1$s, %2$s, %3$s: the three tokens, already wrapped in <code>. */
					esc_html__( 'Type a number, or one of these tokens to have it worked out for you: %1$s products in view, %2$s products in the whole catalogue, %3$s number of product categories.', 'avanam' ),
					'<code>{count}</code>',
					'<code>{total}</code>',
					'<code>{categories}</code>'
				);
				?>
			</p>
			<table class="form-table" role="presentation">
				<?php for ( $i = 1; $i <= AVANAM_CI_STAT_SLOTS; $i++ ) : ?>
					<tr>
						<th scope="row"><?php printf( esc_html__( 'Counter %d', 'avanam' ), (int) $i ); ?></th>
						<td>
							<input type="text" name="<?php echo esc_attr( "{$name}[stat_{$i}_value]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( "stat_{$i}_value" ) ); ?>" placeholder="<?php esc_attr_e( 'Value', 'avanam' ); ?>" style="width:12em">
							<input type="text" class="regular-text" name="<?php echo esc_attr( "{$name}[stat_{$i}_label]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( "stat_{$i}_label" ) ); ?>" placeholder="<?php esc_attr_e( 'Label', 'avanam' ); ?>">
						</td>
					</tr>
				<?php endfor; ?>
			</table>

			<h2 class="title"><?php esc_html_e( 'Toolbar and grid', 'avanam' ); ?></h2>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><?php esc_html_e( 'Show', 'avanam' ); ?></th>
					<td>
						<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[search]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'search' ) ); ?>> <?php esc_html_e( 'Search box', 'avanam' ); ?></label>
						<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[chips]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'chips' ) ); ?>> <?php esc_html_e( 'Category chips', 'avanam' ); ?></label>
						<label style="display:block;margin-left:22px"><input type="checkbox" name="<?php echo esc_attr( "{$name}[chip_counts]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'chip_counts' ) ); ?>> <?php esc_html_e( 'with product counts', 'avanam' ); ?></label>
						<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[result_count]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'result_count' ) ); ?>> <?php esc_html_e( '"12 of 55 shown" count', 'avanam' ); ?></label>
						<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[sorting]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'sorting' ) ); ?>> <?php esc_html_e( 'Sort dropdown', 'avanam' ); ?></label>
					</td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-all"><?php esc_html_e( '"All" chip label', 'avanam' ); ?></label></th>
					<td><input id="ci-all" type="text" name="<?php echo esc_attr( "{$name}[chips_label]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'chips_label' ) ); ?>"></td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-cols"><?php esc_html_e( 'Columns', 'avanam' ); ?></label></th>
					<td><input id="ci-cols" type="number" min="2" max="4" class="small-text" name="<?php echo esc_attr( "{$name}[columns]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'columns' ) ); ?>"></td>
				</tr>
			</table>

			<h2 class="title"><?php esc_html_e( 'Card details', 'avanam' ); ?></h2>
			<p class="description" style="max-width:60em">
				<?php esc_html_e( 'Cards read existing WooCommerce product attributes - nothing is added to your products. Set attributes up under Products - Attributes and assign them on each product as usual.', 'avanam' ); ?>
			</p>
			<table class="form-table" role="presentation">
				<?php if ( ! $attrs ) : ?>
					<tr>
						<th scope="row"><?php esc_html_e( 'Attributes', 'avanam' ); ?></th>
						<td>
							<p class="description">
								<?php esc_html_e( 'No global product attributes exist yet. Create some under Products - Attributes and they will appear here. Until then cards show the product price.', 'avanam' ); ?>
							</p>
						</td>
					</tr>
				<?php else : ?>
					<tr>
						<th scope="row"><?php esc_html_e( 'Spec line', 'avanam' ); ?></th>
						<td>
							<?php foreach ( $attrs as $taxonomy => $label ) : ?>
								<label style="display:block">
									<input type="checkbox" name="<?php echo esc_attr( "{$name}[spec_attrs][]" ); ?>" value="<?php echo esc_attr( $taxonomy ); ?>" <?php checked( in_array( $taxonomy, (array) avanam_ci_option( 'spec_attrs' ), true ) ); ?>>
									<?php echo esc_html( $label ); ?>
								</label>
							<?php endforeach; ?>
							<p class="description"><?php esc_html_e( 'Joined with a dot on the small grey line under the product name.', 'avanam' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Data rows', 'avanam' ); ?></th>
						<td>
							<?php foreach ( $attrs as $taxonomy => $label ) : ?>
								<label style="display:block">
									<input type="checkbox" name="<?php echo esc_attr( "{$name}[row_attrs][]" ); ?>" value="<?php echo esc_attr( $taxonomy ); ?>" <?php checked( in_array( $taxonomy, (array) avanam_ci_option( 'row_attrs' ), true ) ); ?>>
									<?php echo esc_html( $label ); ?>
								</label>
							<?php endforeach; ?>
							<p class="description"><?php esc_html_e( 'Each becomes a label / value row, like Purity and Latest lot in the design.', 'avanam' ); ?></p>
						</td>
					</tr>
				<?php endif; ?>
				<tr>
					<th scope="row"><label for="ci-badge"><?php esc_html_e( 'Status badge', 'avanam' ); ?></label></th>
					<td>
						<input id="ci-badge" type="text" name="<?php echo esc_attr( "{$name}[badge]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'badge' ) ); ?>">
						<p class="description"><?php esc_html_e( 'Highlighted badge in the top-left of every card. Leave blank for none. The plain badge in the top-right comes from each category\'s own "Card badge" field.', 'avanam' ); ?></p>
					</td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-link"><?php esc_html_e( 'Card link text', 'avanam' ); ?></label></th>
					<td><input id="ci-link" type="text" name="<?php echo esc_attr( "{$name}[link_label]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'link_label' ) ); ?>"></td>
				</tr>
			</table>

			<h2 class="title"><?php esc_html_e( 'Closing panel', 'avanam' ); ?></h2>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><?php esc_html_e( 'Panel', 'avanam' ); ?></th>
					<td><label><input type="checkbox" name="<?php echo esc_attr( "{$name}[cta]" ); ?>" value="yes" <?php checked( avanam_ci_on( 'cta' ) ); ?>> <?php esc_html_e( 'Show below the grid', 'avanam' ); ?></label></td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-cta-title"><?php esc_html_e( 'Heading', 'avanam' ); ?></label></th>
					<td><input id="ci-cta-title" class="regular-text" type="text" name="<?php echo esc_attr( "{$name}[cta_title]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'cta_title' ) ); ?>"></td>
				</tr>
				<tr>
					<th scope="row"><label for="ci-cta-text"><?php esc_html_e( 'Text', 'avanam' ); ?></label></th>
					<td><textarea id="ci-cta-text" class="large-text" rows="2" name="<?php echo esc_attr( "{$name}[cta_text]" ); ?>"><?php echo esc_textarea( avanam_ci_option( 'cta_text' ) ); ?></textarea></td>
				</tr>
				<tr>
					<th scope="row"><?php esc_html_e( 'Button', 'avanam' ); ?></th>
					<td>
						<input type="text" name="<?php echo esc_attr( "{$name}[cta_button]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'cta_button' ) ); ?>" placeholder="<?php esc_attr_e( 'Label', 'avanam' ); ?>">
						<input type="url" class="regular-text" name="<?php echo esc_attr( "{$name}[cta_url]" ); ?>" value="<?php echo esc_attr( avanam_ci_option( 'cta_url' ) ); ?>" placeholder="<?php esc_attr_e( 'Leave blank to link to the shop', 'avanam' ); ?>">
					</td>
				</tr>
			</table>

			<?php submit_button(); ?>
		</form>
	</div>
	<?php
}
