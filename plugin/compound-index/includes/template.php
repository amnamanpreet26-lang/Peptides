<?php
/**
 * Swaps in the Compound Index archive template and supplies the data it needs.
 *
 * The product loop itself is left completely alone - it is still WooCommerce's
 * main query, so a category archive shows that category's products, search
 * works, sorting works and pagination works.
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

/**
 * Archive template controller.
 */
class Compound_Index_Template {

	/**
	 * Hook everything up.
	 */
	public static function init() {
		add_filter( 'template_include', array( __CLASS__, 'template_include' ), 99 );
		add_action( 'wp_enqueue_scripts', array( __CLASS__, 'assets' ) );
		add_filter( 'woocommerce_catalog_orderby', array( __CLASS__, 'orderby_options' ) );
	}

	/**
	 * Is the Compound Index layout in charge of this request?
	 *
	 * @return bool
	 */
	public static function is_active() {
		if ( is_admin() || ! function_exists( 'is_shop' ) ) {
			return false;
		}

		$active = false;

		if ( is_shop() && ! is_search() ) {
			$active = Compound_Index_Settings::on( 'enable_shop' );
		} elseif ( is_product_category() ) {
			$active = Compound_Index_Settings::on( 'enable_category' );
		} elseif ( is_product_tag() ) {
			$active = Compound_Index_Settings::on( 'enable_tag' );
		} elseif ( is_search() && 'product' === get_query_var( 'post_type' ) ) {
			$active = Compound_Index_Settings::on( 'enable_shop' );
		}

		/**
		 * Filters whether the Compound Index layout takes over this request.
		 *
		 * @param bool $active Current decision.
		 */
		return (bool) apply_filters( 'compound_index_is_active', $active );
	}

	/**
	 * Point WordPress at our archive template.
	 *
	 * Runs at priority 99 so it lands after WooCommerce's own template loader.
	 *
	 * @param string $template Template WordPress resolved.
	 * @return string
	 */
	public static function template_include( $template ) {
		if ( ! self::is_active() ) {
			return $template;
		}

		// We print our own title, breadcrumb, result count, sorting and pagination.
		if ( Compound_Index_Settings::on( 'hide_theme_breadcrumb' ) ) {
			remove_action( 'woocommerce_before_main_content', 'woocommerce_breadcrumb', 20 );
			add_filter( 'woocommerce_show_page_title', '__return_false' );
		}
		remove_action( 'woocommerce_before_shop_loop', 'woocommerce_result_count', 20 );
		remove_action( 'woocommerce_before_shop_loop', 'woocommerce_catalog_ordering', 30 );
		remove_action( 'woocommerce_after_shop_loop', 'woocommerce_pagination', 10 );

		$override = locate_template( array( 'compound-index/archive-product.php' ) );

		return $override ? $override : COMPOUND_INDEX_PATH . 'templates/archive-product.php';
	}

	/**
	 * Load the stylesheet only where the layout runs.
	 */
	public static function assets() {
		if ( ! self::is_active() ) {
			return;
		}

		wp_enqueue_style(
			'compound-index',
			COMPOUND_INDEX_URL . 'assets/compound-index.css',
			array(),
			COMPOUND_INDEX_VERSION
		);

		wp_enqueue_script(
			'compound-index',
			COMPOUND_INDEX_URL . 'assets/compound-index.js',
			array(),
			COMPOUND_INDEX_VERSION,
			true
		);
	}

	/**
	 * Add alphabetical sorting, which the design uses and WooCommerce omits.
	 *
	 * WC_Query already understands "title" and "title-desc"; they are simply
	 * missing from the default dropdown.
	 *
	 * @param array $options Existing sort options.
	 * @return array
	 */
	public static function orderby_options( $options ) {
		return array_merge(
			$options,
			array(
				'title'      => __( 'Name A-Z', 'compound-index' ),
				'title-desc' => __( 'Name Z-A', 'compound-index' ),
			)
		);
	}

	/**
	 * Heading for the archive.
	 *
	 * @return string
	 */
	public static function title() {
		if ( 'archive' === Compound_Index_Settings::get( 'title_mode' ) ) {
			if ( is_search() ) {
				/* translators: %s: search term. */
				return sprintf( __( 'Results for %s', 'compound-index' ), get_search_query() );
			}
			return wp_strip_all_tags( woocommerce_page_title( false ) );
		}

		return Compound_Index_Settings::get( 'title' );
	}

	/**
	 * Intro copy: the category description when there is one, else the setting.
	 *
	 * @return string
	 */
	public static function intro() {
		if ( is_product_taxonomy() ) {
			$term = get_queried_object();
			if ( $term instanceof WP_Term && '' !== trim( (string) $term->description ) ) {
				return $term->description;
			}
		}

		return Compound_Index_Settings::get( 'intro' );
	}

	/**
	 * Breadcrumb trail. The last entry has an empty url.
	 *
	 * @return array List of array{label:string,url:string}.
	 */
	public static function breadcrumb() {
		$trail = array(
			array(
				'label' => __( 'Home', 'compound-index' ),
				'url'   => home_url( '/' ),
			),
		);

		if ( is_product_taxonomy() ) {
			$shop = wc_get_page_permalink( 'shop' );
			if ( $shop ) {
				$trail[] = array(
					'label' => __( 'Shop', 'compound-index' ),
					'url'   => $shop,
				);
			}
		}

		$trail[] = array(
			'label' => self::title(),
			'url'   => '',
		);

		/**
		 * Filters the archive breadcrumb trail.
		 *
		 * @param array $trail List of label/url pairs.
		 */
		return apply_filters( 'compound_index_breadcrumb', $trail );
	}

	/**
	 * The four header counters, already formatted for display.
	 *
	 * @return array List of array{value:string,label:string}.
	 */
	public static function stats() {
		$out = array();

		foreach ( (array) Compound_Index_Settings::get( 'stats', array() ) as $stat ) {
			$value = Compound_Index_Stats::display( $stat );
			$label = isset( $stat['label'] ) ? $stat['label'] : '';

			if ( '' === $value || '' === $label ) {
				continue;
			}

			$out[] = array(
				'value' => $value,
				'label' => $label,
			);
		}

		return $out;
	}

	/**
	 * Category filter chips.
	 *
	 * Every chip is a plain link to a WooCommerce category archive, so the grid
	 * it lands on is always the real product query for that category.
	 *
	 * @return array List of array{label:string,url:string,count:int,active:bool}.
	 */
	public static function chips() {
		if ( ! Compound_Index_Settings::on( 'chips_enabled' ) ) {
			return array();
		}

		$current = 0;
		if ( is_product_category() ) {
			$term    = get_queried_object();
			$current = $term instanceof WP_Term ? (int) $term->term_id : 0;
		}

		$chips = array(
			array(
				'label'  => Compound_Index_Settings::get( 'chips_all_label' ),
				'url'    => wc_get_page_permalink( 'shop' ),
				'count'  => null,
				'active' => ! $current,
			),
		);

		$args = array(
			'taxonomy'   => 'product_cat',
			'hide_empty' => true,
			'orderby'    => 'name',
		);

		if ( 'custom' === Compound_Index_Settings::get( 'chips_source' ) ) {
			$picked = array_filter( (array) Compound_Index_Settings::get( 'chips_terms', array() ) );
			if ( ! $picked ) {
				return $chips;
			}
			$args['include']    = $picked;
			$args['hide_empty'] = false;
			$args['orderby']    = 'include';
		} else {
			$args['parent'] = 0;
		}

		$terms = get_terms( $args );
		if ( is_wp_error( $terms ) ) {
			return $chips;
		}

		foreach ( $terms as $term ) {
			$url = get_term_link( $term );
			if ( is_wp_error( $url ) ) {
				continue;
			}

			$chips[] = array(
				'label'  => $term->name,
				'url'    => $url,
				'count'  => (int) $term->count,
				'active' => $current === (int) $term->term_id,
			);
		}

		/**
		 * Filters the category chips shown above the grid.
		 *
		 * @param array $chips Chip definitions.
		 */
		return apply_filters( 'compound_index_chips', $chips );
	}

	/**
	 * Badges for one product card.
	 *
	 * @param WC_Product $product Product.
	 * @return array List of array{label:string,tone:string}.
	 */
	public static function badges( $product ) {
		$badges = array();
		$mode   = Compound_Index_Settings::get( 'badge_left_mode' );

		if ( 'off' !== $mode ) {
			$show = ( 'always' === $mode );

			if ( 'meta' === $mode ) {
				$key  = Compound_Index_Settings::get( 'badge_left_meta' );
				$show = ( '' !== Compound_Index_Product_Meta::get( $product, $key ) );
			}

			if ( $show ) {
				$badges[] = array(
					'label' => Compound_Index_Settings::get( 'badge_left_label' ),
					'tone'  => 'primary',
				);
			}
		}

		$flagged = array_filter( (array) Compound_Index_Settings::get( 'badge_right_terms', array() ) );
		if ( $flagged ) {
			foreach ( $flagged as $term_id ) {
				if ( has_term( (int) $term_id, 'product_cat', $product->get_id() ) ) {
					$term = get_term( (int) $term_id, 'product_cat' );
					if ( $term instanceof WP_Term ) {
						$badges[] = array(
							'label' => $term->name,
							'tone'  => 'plain',
						);
					}
					break;
				}
			}
		}

		/**
		 * Filters the badges on a compound card.
		 *
		 * @param array      $badges  Badge definitions.
		 * @param WC_Product $product Product being rendered.
		 */
		return apply_filters( 'compound_index_badges', $badges, $product );
	}

	/**
	 * "12 of 55 shown" for the toolbar.
	 *
	 * @return string
	 */
	public static function result_count() {
		global $wp_query;

		$total = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : 0;
		$shown = isset( $wp_query->post_count ) ? (int) $wp_query->post_count : 0;

		if ( ! $total ) {
			return '';
		}

		return sprintf(
			/* translators: 1: products on this page, 2: products in total. */
			__( '%1$s of %2$s shown', 'compound-index' ),
			number_format_i18n( $shown ),
			number_format_i18n( $total )
		);
	}

	/**
	 * Hidden inputs that keep the current category when searching.
	 */
	public static function search_hidden_fields() {
		echo '<input type="hidden" name="post_type" value="product">';

		if ( is_product_category() ) {
			$term = get_queried_object();
			if ( $term instanceof WP_Term ) {
				echo '<input type="hidden" name="product_cat" value="' . esc_attr( $term->slug ) . '">';
			}
		}
	}
}
