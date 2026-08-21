<?php
/**
 * Admin settings for the Compound Index archive layout.
 *
 * Everything the layout renders - the header copy, the four stat counters, the
 * category chips and their counts, the badges and the closing CTA - is set here
 * rather than in code.
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

/**
 * Settings screen and option access.
 */
class Compound_Index_Settings {

	const OPTION = 'compound_index_settings';

	/**
	 * Memoised merged settings.
	 *
	 * @var array|null
	 */
	private static $cache = null;

	/**
	 * Hook the admin screen up.
	 */
	public static function init() {
		add_action( 'admin_menu', array( __CLASS__, 'menu' ) );
		add_action( 'admin_init', array( __CLASS__, 'register' ) );
		add_filter( 'plugin_action_links_' . plugin_basename( COMPOUND_INDEX_FILE ), array( __CLASS__, 'action_link' ) );
	}

	/**
	 * Stat counter sources offered in the dropdown.
	 *
	 * @return array
	 */
	public static function stat_sources() {
		return array(
			'manual'          => __( 'Fixed value I type below', 'compound-index' ),
			'product_count'   => __( 'Number of products in this archive', 'compound-index' ),
			'catalog_count'   => __( 'Number of products in the whole catalogue', 'compound-index' ),
			'term_count'      => __( 'Number of product categories', 'compound-index' ),
			'meta_avg'        => __( 'Average of a product field', 'compound-index' ),
			'meta_median'     => __( 'Median of a product field', 'compound-index' ),
			'meta_filled_pct' => __( 'Percent of products with a field filled in', 'compound-index' ),
		);
	}

	/**
	 * Default settings, matching the reference design.
	 *
	 * @return array
	 */
	public static function defaults() {
		return array(
			'enable_shop'           => 'yes',
			'enable_category'       => 'yes',
			'enable_tag'            => 'no',
			'hide_theme_breadcrumb' => 'yes',

			'show_breadcrumb'       => 'yes',
			'title_mode'            => 'custom',
			'title'                 => __( 'Compound index', 'compound-index' ),
			'intro'                 => __( 'Every compound we produce, with its current specification and the lot most recently released. Open any entry for the full data sheet, certificate of analysis and handling notes.', 'compound-index' ),

			'stats'                 => array(
				array(
					'source'   => 'product_count',
					'value'    => '',
					'suffix'   => '',
					'label'    => __( 'Compounds listed', 'compound-index' ),
					'meta_key' => '',
					'decimals' => '0',
				),
				array(
					'source'   => 'meta_median',
					'value'    => '',
					'suffix'   => '%',
					'label'    => __( 'Median purity', 'compound-index' ),
					'meta_key' => '_ci_purity',
					'decimals' => '1',
				),
				array(
					'source'   => 'meta_filled_pct',
					'value'    => '',
					'suffix'   => '%',
					'label'    => __( 'Lots with a COA', 'compound-index' ),
					'meta_key' => '_ci_coa_url',
					'decimals' => '0',
				),
				array(
					'source'   => 'manual',
					'value'    => '36',
					'suffix'   => ' mo',
					'label'    => __( 'Records retained', 'compound-index' ),
					'meta_key' => '',
					'decimals' => '0',
				),
			),

			'chips_enabled'         => 'yes',
			'chips_source'          => 'top_level',
			'chips_terms'           => array(),
			'chips_show_count'      => 'yes',
			'chips_all_label'       => __( 'All', 'compound-index' ),

			'search_enabled'        => 'yes',
			'search_placeholder'    => __( 'Search by name, sequence or CAS', 'compound-index' ),
			'count_enabled'         => 'yes',
			'sort_enabled'          => 'yes',
			'columns'               => '3',

			'badge_left_mode'       => 'meta',
			'badge_left_label'      => __( 'Documented', 'compound-index' ),
			'badge_left_meta'       => '_ci_coa_url',
			'badge_right_terms'     => array(),

			'cta_enabled'           => 'yes',
			'cta_title'             => __( 'Looking for something not listed?', 'compound-index' ),
			'cta_text'              => __( 'The full index runs to every compound we hold, each with its own specification and certificate.', 'compound-index' ),
			'cta_button_label'      => __( 'Browse all products', 'compound-index' ),
			'cta_button_url'        => '',
		);
	}

	/**
	 * All settings, defaults merged in.
	 *
	 * @return array
	 */
	public static function all() {
		if ( null === self::$cache ) {
			$saved = get_option( self::OPTION, array() );
			if ( ! is_array( $saved ) ) {
				$saved = array();
			}
			self::$cache = wp_parse_args( $saved, self::defaults() );

			// Stats is a fixed-length list; make sure every slot exists.
			$defaults = self::defaults();
			foreach ( $defaults['stats'] as $i => $slot ) {
				if ( empty( self::$cache['stats'][ $i ] ) || ! is_array( self::$cache['stats'][ $i ] ) ) {
					self::$cache['stats'][ $i ] = $slot;
				} else {
					self::$cache['stats'][ $i ] = wp_parse_args( self::$cache['stats'][ $i ], $slot );
				}
			}
		}

		return self::$cache;
	}

	/**
	 * Read one setting.
	 *
	 * @param string $key     Setting key.
	 * @param mixed  $default Returned when the key is missing.
	 * @return mixed
	 */
	public static function get( $key, $default = '' ) {
		$all = self::all();
		return array_key_exists( $key, $all ) ? $all[ $key ] : $default;
	}

	/**
	 * Convenience boolean read.
	 *
	 * @param string $key Setting key.
	 * @return bool
	 */
	public static function on( $key ) {
		return 'yes' === self::get( $key );
	}

	/**
	 * Add the submenu page under Products.
	 */
	public static function menu() {
		add_submenu_page(
			'edit.php?post_type=product',
			__( 'Compound Index', 'compound-index' ),
			__( 'Compound Index', 'compound-index' ),
			'manage_woocommerce',
			'compound-index',
			array( __CLASS__, 'render' )
		);
	}

	/**
	 * Add a Settings link on the plugins screen.
	 *
	 * @param array $links Existing links.
	 * @return array
	 */
	public static function action_link( $links ) {
		$url = admin_url( 'edit.php?post_type=product&page=compound-index' );
		array_unshift( $links, '<a href="' . esc_url( $url ) . '">' . esc_html__( 'Settings', 'compound-index' ) . '</a>' );
		return $links;
	}

	/**
	 * Register the option with its sanitiser.
	 */
	public static function register() {
		register_setting(
			'compound_index',
			self::OPTION,
			array(
				'type'              => 'array',
				'sanitize_callback' => array( __CLASS__, 'sanitize' ),
				'default'           => self::defaults(),
			)
		);
	}

	/**
	 * Sanitise submitted settings.
	 *
	 * @param mixed $input Raw form input.
	 * @return array
	 */
	public static function sanitize( $input ) {
		$defaults = self::defaults();
		$out      = array();

		if ( ! is_array( $input ) ) {
			$input = array();
		}

		$checkboxes = array(
			'enable_shop',
			'enable_category',
			'enable_tag',
			'hide_theme_breadcrumb',
			'show_breadcrumb',
			'chips_enabled',
			'chips_show_count',
			'search_enabled',
			'count_enabled',
			'sort_enabled',
			'cta_enabled',
		);
		foreach ( $checkboxes as $key ) {
			$out[ $key ] = empty( $input[ $key ] ) ? 'no' : 'yes';
		}

		$plain = array(
			'title',
			'chips_all_label',
			'search_placeholder',
			'badge_left_label',
			'cta_title',
			'cta_button_label',
		);
		foreach ( $plain as $key ) {
			$out[ $key ] = isset( $input[ $key ] ) ? sanitize_text_field( wp_unslash( $input[ $key ] ) ) : $defaults[ $key ];
		}

		$out['intro']            = isset( $input['intro'] ) ? wp_kses_post( wp_unslash( $input['intro'] ) ) : $defaults['intro'];
		$out['cta_text']         = isset( $input['cta_text'] ) ? wp_kses_post( wp_unslash( $input['cta_text'] ) ) : $defaults['cta_text'];
		$out['cta_button_url']   = isset( $input['cta_button_url'] ) ? esc_url_raw( wp_unslash( $input['cta_button_url'] ) ) : '';
		$out['badge_left_meta']  = isset( $input['badge_left_meta'] ) ? sanitize_key( wp_unslash( $input['badge_left_meta'] ) ) : $defaults['badge_left_meta'];
		$out['title_mode']       = ( isset( $input['title_mode'] ) && 'archive' === $input['title_mode'] ) ? 'archive' : 'custom';
		$out['chips_source']     = ( isset( $input['chips_source'] ) && 'custom' === $input['chips_source'] ) ? 'custom' : 'top_level';
		$out['badge_left_mode']  = in_array( ( $input['badge_left_mode'] ?? '' ), array( 'meta', 'always', 'off' ), true ) ? $input['badge_left_mode'] : 'meta';
		$out['columns']          = max( 2, min( 4, absint( $input['columns'] ?? 3 ) ) );
		$out['chips_terms']      = array_map( 'absint', (array) ( $input['chips_terms'] ?? array() ) );
		$out['badge_right_terms'] = array_map( 'absint', (array) ( $input['badge_right_terms'] ?? array() ) );

		$sources     = array_keys( self::stat_sources() );
		$out['stats'] = array();
		foreach ( $defaults['stats'] as $i => $slot ) {
			$raw = isset( $input['stats'][ $i ] ) && is_array( $input['stats'][ $i ] ) ? $input['stats'][ $i ] : array();

			$out['stats'][ $i ] = array(
				'source'   => in_array( ( $raw['source'] ?? '' ), $sources, true ) ? $raw['source'] : 'manual',
				'value'    => sanitize_text_field( wp_unslash( $raw['value'] ?? '' ) ),
				'suffix'   => sanitize_text_field( wp_unslash( $raw['suffix'] ?? '' ) ),
				'label'    => sanitize_text_field( wp_unslash( $raw['label'] ?? '' ) ),
				'meta_key' => sanitize_key( wp_unslash( $raw['meta_key'] ?? '' ) ),
				'decimals' => (string) min( 3, absint( $raw['decimals'] ?? 0 ) ),
			);
		}

		Compound_Index_Stats::flush_cache();
		self::$cache = null;

		return $out;
	}

	/**
	 * Render the settings screen.
	 */
	public static function render() {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			return;
		}

		$s     = self::all();
		$name  = self::OPTION;
		$terms = get_terms(
			array(
				'taxonomy'   => 'product_cat',
				'hide_empty' => false,
			)
		);
		if ( is_wp_error( $terms ) ) {
			$terms = array();
		}
		?>
		<div class="wrap compound-index-settings">
			<h1><?php esc_html_e( 'Compound Index', 'compound-index' ); ?></h1>
			<p class="description" style="max-width:64em">
				<?php esc_html_e( 'Controls the shop and product-category archive layout. Products themselves always come from WooCommerce - this screen only changes how the archive is presented.', 'compound-index' ); ?>
			</p>

			<form method="post" action="options.php">
				<?php settings_fields( 'compound_index' ); ?>

				<h2 class="title"><?php esc_html_e( 'Where the layout applies', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Use on', 'compound-index' ); ?></th>
						<td>
							<?php
							$where = array(
								'enable_shop'     => __( 'Main shop page', 'compound-index' ),
								'enable_category' => __( 'Product category archives', 'compound-index' ),
								'enable_tag'      => __( 'Product tag archives', 'compound-index' ),
							);
							foreach ( $where as $key => $label ) :
								?>
								<label style="display:block;margin-bottom:4px">
									<input type="checkbox" name="<?php echo esc_attr( "{$name}[{$key}]" ); ?>" value="yes" <?php checked( $s[ $key ], 'yes' ); ?>>
									<?php echo esc_html( $label ); ?>
								</label>
							<?php endforeach; ?>
							<p class="description"><?php esc_html_e( 'Turn all three off to hand the archive back to your theme.', 'compound-index' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Theme breadcrumb', 'compound-index' ); ?></th>
						<td>
							<label>
								<input type="checkbox" name="<?php echo esc_attr( "{$name}[hide_theme_breadcrumb]" ); ?>" value="yes" <?php checked( $s['hide_theme_breadcrumb'], 'yes' ); ?>>
								<?php esc_html_e( "Hide the theme's own breadcrumb and page title on these archives", 'compound-index' ); ?>
							</label>
							<p class="description"><?php esc_html_e( 'Leave this on unless you end up with no breadcrumb at all - some themes print theirs outside WooCommerce.', 'compound-index' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-columns"><?php esc_html_e( 'Columns', 'compound-index' ); ?></label></th>
						<td>
							<input id="ci-columns" type="number" min="2" max="4" name="<?php echo esc_attr( "{$name}[columns]" ); ?>" value="<?php echo esc_attr( $s['columns'] ); ?>" class="small-text">
							<p class="description"><?php esc_html_e( 'Products per row on desktop. The design uses 3.', 'compound-index' ); ?></p>
						</td>
					</tr>
				</table>

				<h2 class="title"><?php esc_html_e( 'Page header', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Breadcrumb', 'compound-index' ); ?></th>
						<td><label><input type="checkbox" name="<?php echo esc_attr( "{$name}[show_breadcrumb]" ); ?>" value="yes" <?php checked( $s['show_breadcrumb'], 'yes' ); ?>> <?php esc_html_e( 'Show', 'compound-index' ); ?></label></td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Title', 'compound-index' ); ?></th>
						<td>
							<label style="display:block;margin-bottom:6px">
								<input type="radio" name="<?php echo esc_attr( "{$name}[title_mode]" ); ?>" value="archive" <?php checked( $s['title_mode'], 'archive' ); ?>>
								<?php esc_html_e( 'Use the archive title (the category name)', 'compound-index' ); ?>
							</label>
							<label style="display:block;margin-bottom:6px">
								<input type="radio" name="<?php echo esc_attr( "{$name}[title_mode]" ); ?>" value="custom" <?php checked( $s['title_mode'], 'custom' ); ?>>
								<?php esc_html_e( 'Always use this title:', 'compound-index' ); ?>
							</label>
							<input type="text" class="regular-text" name="<?php echo esc_attr( "{$name}[title]" ); ?>" value="<?php echo esc_attr( $s['title'] ); ?>">
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-intro"><?php esc_html_e( 'Intro text', 'compound-index' ); ?></label></th>
						<td>
							<textarea id="ci-intro" class="large-text" rows="3" name="<?php echo esc_attr( "{$name}[intro]" ); ?>"><?php echo esc_textarea( $s['intro'] ); ?></textarea>
							<p class="description"><?php esc_html_e( 'On a category archive the category description is used instead, when it has one.', 'compound-index' ); ?></p>
						</td>
					</tr>
				</table>

				<h2 class="title"><?php esc_html_e( 'Counters', 'compound-index' ); ?></h2>
				<p class="description" style="max-width:64em">
					<?php esc_html_e( 'The four figures under the intro. Each one is either a number you type or a figure worked out from your products - counts update on their own as the catalogue changes.', 'compound-index' ); ?>
				</p>
				<table class="widefat striped" style="max-width:1100px;margin:12px 0 24px">
					<thead>
						<tr>
							<th style="width:26%"><?php esc_html_e( 'Where the number comes from', 'compound-index' ); ?></th>
							<th style="width:20%"><?php esc_html_e( 'Product field', 'compound-index' ); ?></th>
							<th style="width:12%"><?php esc_html_e( 'Fixed value', 'compound-index' ); ?></th>
							<th style="width:10%"><?php esc_html_e( 'Suffix', 'compound-index' ); ?></th>
							<th style="width:8%"><?php esc_html_e( 'Decimals', 'compound-index' ); ?></th>
							<th><?php esc_html_e( 'Label', 'compound-index' ); ?></th>
						</tr>
					</thead>
					<tbody>
					<?php foreach ( $s['stats'] as $i => $stat ) : ?>
						<tr>
							<td>
								<select name="<?php echo esc_attr( "{$name}[stats][{$i}][source]" ); ?>" style="width:100%">
									<?php foreach ( self::stat_sources() as $key => $label ) : ?>
										<option value="<?php echo esc_attr( $key ); ?>" <?php selected( $stat['source'], $key ); ?>><?php echo esc_html( $label ); ?></option>
									<?php endforeach; ?>
								</select>
							</td>
							<td>
								<select name="<?php echo esc_attr( "{$name}[stats][{$i}][meta_key]" ); ?>" style="width:100%">
									<option value=""><?php esc_html_e( '- none -', 'compound-index' ); ?></option>
									<?php foreach ( Compound_Index_Product_Meta::fields() as $key => $field ) : ?>
										<option value="<?php echo esc_attr( $key ); ?>" <?php selected( $stat['meta_key'], $key ); ?>><?php echo esc_html( $field['label'] ); ?></option>
									<?php endforeach; ?>
								</select>
							</td>
							<td><input type="text" name="<?php echo esc_attr( "{$name}[stats][{$i}][value]" ); ?>" value="<?php echo esc_attr( $stat['value'] ); ?>" style="width:100%"></td>
							<td><input type="text" name="<?php echo esc_attr( "{$name}[stats][{$i}][suffix]" ); ?>" value="<?php echo esc_attr( $stat['suffix'] ); ?>" style="width:100%"></td>
							<td><input type="number" min="0" max="3" name="<?php echo esc_attr( "{$name}[stats][{$i}][decimals]" ); ?>" value="<?php echo esc_attr( $stat['decimals'] ); ?>" style="width:100%"></td>
							<td><input type="text" name="<?php echo esc_attr( "{$name}[stats][{$i}][label]" ); ?>" value="<?php echo esc_attr( $stat['label'] ); ?>" style="width:100%"></td>
						</tr>
					<?php endforeach; ?>
					</tbody>
				</table>

				<h2 class="title"><?php esc_html_e( 'Category chips', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Chips', 'compound-index' ); ?></th>
						<td>
							<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[chips_enabled]" ); ?>" value="yes" <?php checked( $s['chips_enabled'], 'yes' ); ?>> <?php esc_html_e( 'Show the category filter row', 'compound-index' ); ?></label>
							<label style="display:block;margin-top:6px"><input type="checkbox" name="<?php echo esc_attr( "{$name}[chips_show_count]" ); ?>" value="yes" <?php checked( $s['chips_show_count'], 'yes' ); ?>> <?php esc_html_e( 'Show the product count on each chip', 'compound-index' ); ?></label>
							<p class="description"><?php esc_html_e( 'Each chip links to that WooCommerce category archive, so the grid below always shows real products from that category.', 'compound-index' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Which categories', 'compound-index' ); ?></th>
						<td>
							<label style="display:block;margin-bottom:6px">
								<input type="radio" name="<?php echo esc_attr( "{$name}[chips_source]" ); ?>" value="top_level" <?php checked( $s['chips_source'], 'top_level' ); ?>>
								<?php esc_html_e( 'All top-level product categories (updates itself)', 'compound-index' ); ?>
							</label>
							<label style="display:block;margin-bottom:6px">
								<input type="radio" name="<?php echo esc_attr( "{$name}[chips_source]" ); ?>" value="custom" <?php checked( $s['chips_source'], 'custom' ); ?>>
								<?php esc_html_e( 'Only the ones I pick:', 'compound-index' ); ?>
							</label>
							<select multiple size="6" name="<?php echo esc_attr( "{$name}[chips_terms][]" ); ?>" style="min-width:320px">
								<?php foreach ( $terms as $term ) : ?>
									<option value="<?php echo esc_attr( $term->term_id ); ?>" <?php selected( in_array( (int) $term->term_id, (array) $s['chips_terms'], true ) ); ?>>
										<?php echo esc_html( $term->name . ' (' . $term->count . ')' ); ?>
									</option>
								<?php endforeach; ?>
							</select>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-all"><?php esc_html_e( '"All" chip label', 'compound-index' ); ?></label></th>
						<td><input id="ci-all" type="text" name="<?php echo esc_attr( "{$name}[chips_all_label]" ); ?>" value="<?php echo esc_attr( $s['chips_all_label'] ); ?>"></td>
					</tr>
				</table>

				<h2 class="title"><?php esc_html_e( 'Toolbar', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Show', 'compound-index' ); ?></th>
						<td>
							<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[search_enabled]" ); ?>" value="yes" <?php checked( $s['search_enabled'], 'yes' ); ?>> <?php esc_html_e( 'Search box', 'compound-index' ); ?></label>
							<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[count_enabled]" ); ?>" value="yes" <?php checked( $s['count_enabled'], 'yes' ); ?>> <?php esc_html_e( '"12 of 55 shown" count', 'compound-index' ); ?></label>
							<label style="display:block"><input type="checkbox" name="<?php echo esc_attr( "{$name}[sort_enabled]" ); ?>" value="yes" <?php checked( $s['sort_enabled'], 'yes' ); ?>> <?php esc_html_e( 'Sort dropdown', 'compound-index' ); ?></label>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-ph"><?php esc_html_e( 'Search placeholder', 'compound-index' ); ?></label></th>
						<td><input id="ci-ph" type="text" class="regular-text" name="<?php echo esc_attr( "{$name}[search_placeholder]" ); ?>" value="<?php echo esc_attr( $s['search_placeholder'] ); ?>"></td>
					</tr>
				</table>

				<h2 class="title"><?php esc_html_e( 'Card badges', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Left badge', 'compound-index' ); ?></th>
						<td>
							<select name="<?php echo esc_attr( "{$name}[badge_left_mode]" ); ?>">
								<option value="meta" <?php selected( $s['badge_left_mode'], 'meta' ); ?>><?php esc_html_e( 'Show when a product field is filled in', 'compound-index' ); ?></option>
								<option value="always" <?php selected( $s['badge_left_mode'], 'always' ); ?>><?php esc_html_e( 'Show on every product', 'compound-index' ); ?></option>
								<option value="off" <?php selected( $s['badge_left_mode'], 'off' ); ?>><?php esc_html_e( 'Never show', 'compound-index' ); ?></option>
							</select>
							<select name="<?php echo esc_attr( "{$name}[badge_left_meta]" ); ?>">
								<?php foreach ( Compound_Index_Product_Meta::fields() as $key => $field ) : ?>
									<option value="<?php echo esc_attr( $key ); ?>" <?php selected( $s['badge_left_meta'], $key ); ?>><?php echo esc_html( $field['label'] ); ?></option>
								<?php endforeach; ?>
							</select>
							<input type="text" name="<?php echo esc_attr( "{$name}[badge_left_label]" ); ?>" value="<?php echo esc_attr( $s['badge_left_label'] ); ?>" placeholder="<?php esc_attr_e( 'Badge text', 'compound-index' ); ?>">
						</td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Right badge', 'compound-index' ); ?></th>
						<td>
							<select multiple size="5" name="<?php echo esc_attr( "{$name}[badge_right_terms][]" ); ?>" style="min-width:320px">
								<?php foreach ( $terms as $term ) : ?>
									<option value="<?php echo esc_attr( $term->term_id ); ?>" <?php selected( in_array( (int) $term->term_id, (array) $s['badge_right_terms'], true ) ); ?>>
										<?php echo esc_html( $term->name ); ?>
									</option>
								<?php endforeach; ?>
							</select>
							<p class="description"><?php esc_html_e( 'Products in any of these categories get a second badge showing that category name - this is how "Blend" appears in the design.', 'compound-index' ); ?></p>
						</td>
					</tr>
				</table>

				<h2 class="title"><?php esc_html_e( 'Closing panel', 'compound-index' ); ?></h2>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><?php esc_html_e( 'Panel', 'compound-index' ); ?></th>
						<td><label><input type="checkbox" name="<?php echo esc_attr( "{$name}[cta_enabled]" ); ?>" value="yes" <?php checked( $s['cta_enabled'], 'yes' ); ?>> <?php esc_html_e( 'Show below the grid', 'compound-index' ); ?></label></td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-cta-t"><?php esc_html_e( 'Heading', 'compound-index' ); ?></label></th>
						<td><input id="ci-cta-t" type="text" class="regular-text" name="<?php echo esc_attr( "{$name}[cta_title]" ); ?>" value="<?php echo esc_attr( $s['cta_title'] ); ?>"></td>
					</tr>
					<tr>
						<th scope="row"><label for="ci-cta-x"><?php esc_html_e( 'Text', 'compound-index' ); ?></label></th>
						<td><textarea id="ci-cta-x" class="large-text" rows="2" name="<?php echo esc_attr( "{$name}[cta_text]" ); ?>"><?php echo esc_textarea( $s['cta_text'] ); ?></textarea></td>
					</tr>
					<tr>
						<th scope="row"><?php esc_html_e( 'Button', 'compound-index' ); ?></th>
						<td>
							<input type="text" name="<?php echo esc_attr( "{$name}[cta_button_label]" ); ?>" value="<?php echo esc_attr( $s['cta_button_label'] ); ?>" placeholder="<?php esc_attr_e( 'Label', 'compound-index' ); ?>">
							<input type="url" class="regular-text" name="<?php echo esc_attr( "{$name}[cta_button_url]" ); ?>" value="<?php echo esc_attr( $s['cta_button_url'] ); ?>" placeholder="<?php echo esc_attr( wc_get_page_permalink( 'shop' ) ); ?>">
							<p class="description"><?php esc_html_e( 'Leave the URL blank to link to the shop page.', 'compound-index' ); ?></p>
						</td>
					</tr>
				</table>

				<?php submit_button(); ?>
			</form>
		</div>
		<?php
	}
}
