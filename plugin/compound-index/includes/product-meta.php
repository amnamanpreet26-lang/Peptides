<?php
/**
 * The per-product data the compound cards display.
 *
 * Adds a "Compound Index" tab to the WooCommerce product data panel so CAS
 * number, molecular weight, purity, latest lot and the COA link are edited in
 * the place people already look.
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

/**
 * Product fields used by the archive cards.
 */
class Compound_Index_Product_Meta {

	/**
	 * Field definitions, keyed by meta key.
	 *
	 * @return array
	 */
	public static function fields() {
		return array(
			'_ci_cas'        => array(
				'label'       => __( 'CAS number', 'compound-index' ),
				'placeholder' => '137525-51-0',
				'description' => __( 'Shown on the card under the product name.', 'compound-index' ),
			),
			'_ci_mol_weight' => array(
				'label'       => __( 'Molecular weight', 'compound-index' ),
				'placeholder' => '1419.5 g/mol',
				'description' => __( 'Shown next to the CAS number.', 'compound-index' ),
			),
			'_ci_spec_line'  => array(
				'label'       => __( 'Spec line override', 'compound-index' ),
				'placeholder' => '5 mg + 5 mg / blended 1:1',
				'description' => __( 'Replaces the CAS and molecular weight line. Use it for blends.', 'compound-index' ),
			),
			'_ci_purity'     => array(
				'label'       => __( 'Purity', 'compound-index' ),
				'placeholder' => '99.4%',
				'description' => __( 'Also feeds the median purity counter in the page header.', 'compound-index' ),
			),
			'_ci_lot'        => array(
				'label'       => __( 'Latest lot', 'compound-index' ),
				'placeholder' => 'B-2408-17',
				'description' => __( 'The most recently released lot number.', 'compound-index' ),
			),
			'_ci_coa_url'    => array(
				'label'       => __( 'Certificate of analysis URL', 'compound-index' ),
				'placeholder' => 'https://',
				'description' => __( 'Filling this in earns the product its "Documented" badge and counts toward the COA figure.', 'compound-index' ),
			),
		);
	}

	/**
	 * Hook into the product data panel.
	 */
	public static function init() {
		add_filter( 'woocommerce_product_data_tabs', array( __CLASS__, 'tab' ) );
		add_action( 'woocommerce_product_data_panels', array( __CLASS__, 'panel' ) );
		add_action( 'woocommerce_process_product_meta', array( __CLASS__, 'save' ) );
	}

	/**
	 * Register the tab.
	 *
	 * @param array $tabs Existing tabs.
	 * @return array
	 */
	public static function tab( $tabs ) {
		$tabs['compound_index'] = array(
			'label'    => __( 'Compound Index', 'compound-index' ),
			'target'   => 'compound_index_product_data',
			'class'    => array(),
			'priority' => 65,
		);

		return $tabs;
	}

	/**
	 * Render the panel.
	 */
	public static function panel() {
		echo '<div id="compound_index_product_data" class="panel woocommerce_options_panel hidden"><div class="options_group">';

		foreach ( self::fields() as $key => $field ) {
			woocommerce_wp_text_input(
				array(
					'id'          => $key,
					'label'       => $field['label'],
					'placeholder' => $field['placeholder'],
					'description' => $field['description'],
					'desc_tip'    => true,
				)
			);
		}

		echo '</div></div>';
	}

	/**
	 * Persist the fields.
	 *
	 * Nonce verification is handled upstream by WooCommerce before this action
	 * fires, so the values only need sanitising here.
	 *
	 * @param int $product_id Product being saved.
	 */
	public static function save( $product_id ) {
		$product = wc_get_product( $product_id );
		if ( ! $product ) {
			return;
		}

		foreach ( array_keys( self::fields() ) as $key ) {
			// phpcs:ignore WordPress.Security.NonceVerification.Missing -- verified by WooCommerce before this hook.
			$raw = isset( $_POST[ $key ] ) ? wp_unslash( $_POST[ $key ] ) : '';
			$val = ( '_ci_coa_url' === $key ) ? esc_url_raw( $raw ) : sanitize_text_field( $raw );
			$product->update_meta_data( $key, $val );
		}

		$product->save();
		Compound_Index_Stats::flush_cache();
	}

	/**
	 * Read one field off a product.
	 *
	 * @param WC_Product $product Product.
	 * @param string     $key     Meta key.
	 * @return string
	 */
	public static function get( $product, $key ) {
		if ( ! $product instanceof WC_Product ) {
			return '';
		}

		return trim( (string) $product->get_meta( $key ) );
	}

	/**
	 * The small line under the product name.
	 *
	 * Uses the override when set, otherwise builds "CAS 1234-56-7 · 1419.5 g/mol"
	 * from whichever of the two fields are filled in.
	 *
	 * @param WC_Product $product Product.
	 * @return string
	 */
	public static function spec_line( $product ) {
		$override = self::get( $product, '_ci_spec_line' );
		if ( '' !== $override ) {
			return $override;
		}

		$parts = array();
		$cas   = self::get( $product, '_ci_cas' );
		$mol   = self::get( $product, '_ci_mol_weight' );

		if ( '' !== $cas ) {
			/* translators: %s: CAS registry number. */
			$parts[] = sprintf( __( 'CAS %s', 'compound-index' ), $cas );
		}
		if ( '' !== $mol ) {
			$parts[] = $mol;
		}

		return implode( ' · ', $parts );
	}

	/**
	 * The two-row data block on the card: label => value.
	 *
	 * @param WC_Product $product Product.
	 * @return array
	 */
	public static function data_rows( $product ) {
		$rows   = array();
		$purity = self::get( $product, '_ci_purity' );
		$lot    = self::get( $product, '_ci_lot' );

		if ( '' !== $purity ) {
			$rows[ __( 'Purity', 'compound-index' ) ] = $purity;
		}
		if ( '' !== $lot ) {
			$rows[ __( 'Latest lot', 'compound-index' ) ] = $lot;
		}

		/**
		 * Filters the data rows shown on a compound card.
		 *
		 * @param array      $rows    Label => value.
		 * @param WC_Product $product Product being rendered.
		 */
		return apply_filters( 'compound_index_card_rows', $rows, $product );
	}
}
