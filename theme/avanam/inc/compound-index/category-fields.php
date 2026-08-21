<?php
/**
 * Header fields on product categories.
 *
 * Products -> Categories -> add or edit a category. Whatever is entered here is
 * what the archive header shows for that category. Nothing is added to products
 * themselves.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

/**
 * How many counters the header shows.
 */
const AVANAM_CI_STAT_SLOTS = 4;

/**
 * The text fields stored against each product category.
 *
 * @return array key => array{label, type, description}
 */
function avanam_ci_category_fields() {
	$fields = array(
		'ci_eyebrow' => array(
			'label'       => __( 'Header eyebrow', 'avanam' ),
			'type'        => 'text',
			'description' => __( 'Small line above the title. Leave blank to hide it.', 'avanam' ),
		),
		'ci_title'   => array(
			'label'       => __( 'Header title', 'avanam' ),
			'type'        => 'text',
			'description' => __( 'Overrides the category name in the header. Leave blank to use the category name.', 'avanam' ),
		),
		'ci_intro'   => array(
			'label'       => __( 'Header intro', 'avanam' ),
			'type'        => 'textarea',
			'description' => __( 'Paragraph under the title. Leave blank to use the category description.', 'avanam' ),
		),
	);

	for ( $i = 1; $i <= AVANAM_CI_STAT_SLOTS; $i++ ) {
		$fields[ 'ci_stat_' . $i . '_value' ] = array(
			'label'       => sprintf( /* translators: %d: counter number. */ __( 'Counter %d - value', 'avanam' ), $i ),
			'type'        => 'text',
			'description' => __( 'A number, or a token: {count}, {total}, {categories}.', 'avanam' ),
		);
		$fields[ 'ci_stat_' . $i . '_label' ] = array(
			'label'       => sprintf( /* translators: %d: counter number. */ __( 'Counter %d - label', 'avanam' ), $i ),
			'type'        => 'text',
			'description' => __( 'The small caption under the number.', 'avanam' ),
		);
	}

	$fields['ci_badge'] = array(
		'label'       => __( 'Card badge', 'avanam' ),
		'type'        => 'text',
		'description' => __( 'Shown in the corner of every product card in this category, e.g. Blend. Leave blank for none.', 'avanam' ),
	);

	return $fields;
}

/**
 * Read one field off a product category.
 *
 * @param int    $term_id Term ID.
 * @param string $key     Field key.
 * @return string
 */
function avanam_ci_term_field( $term_id, $key ) {
	if ( ! $term_id ) {
		return '';
	}

	return trim( (string) get_term_meta( $term_id, $key, true ) );
}

/**
 * Fields on the "add category" form.
 */
function avanam_ci_add_form_fields() {
	echo '<div class="form-field"><h2 style="margin:1em 0 .4em">' . esc_html__( 'Compound Index header', 'avanam' ) . '</h2></div>';

	foreach ( avanam_ci_category_fields() as $key => $field ) {
		echo '<div class="form-field">';
		printf( '<label for="%1$s">%2$s</label>', esc_attr( $key ), esc_html( $field['label'] ) );

		if ( 'textarea' === $field['type'] ) {
			printf( '<textarea name="%1$s" id="%1$s" rows="4"></textarea>', esc_attr( $key ) );
		} else {
			printf( '<input type="text" name="%1$s" id="%1$s" value="">', esc_attr( $key ) );
		}

		printf( '<p>%s</p>', esc_html( $field['description'] ) );
		echo '</div>';
	}
}
add_action( 'product_cat_add_form_fields', 'avanam_ci_add_form_fields', 20 );

/**
 * Fields on the "edit category" form.
 *
 * @param WP_Term $term Term being edited.
 */
function avanam_ci_edit_form_fields( $term ) {
	echo '<tr class="form-field"><th colspan="2"><h2 style="margin:1.2em 0 0">' . esc_html__( 'Compound Index header', 'avanam' ) . '</h2>';
	echo '<p class="description">' . esc_html__( 'What this category shows in the archive header. Blank fields fall back to the shop defaults under Products - Compound Index.', 'avanam' ) . '</p></th></tr>';

	foreach ( avanam_ci_category_fields() as $key => $field ) {
		$value = avanam_ci_term_field( $term->term_id, $key );

		echo '<tr class="form-field">';
		printf( '<th scope="row"><label for="%1$s">%2$s</label></th><td>', esc_attr( $key ), esc_html( $field['label'] ) );

		if ( 'textarea' === $field['type'] ) {
			printf( '<textarea name="%1$s" id="%1$s" rows="4" cols="50">%2$s</textarea>', esc_attr( $key ), esc_textarea( $value ) );
		} else {
			printf( '<input type="text" name="%1$s" id="%1$s" value="%2$s" size="40">', esc_attr( $key ), esc_attr( $value ) );
		}

		printf( '<p class="description">%s</p></td></tr>', esc_html( $field['description'] ) );
	}
}
add_action( 'product_cat_edit_form_fields', 'avanam_ci_edit_form_fields', 20 );

/**
 * Save the fields.
 *
 * WordPress verifies the term nonce before these hooks fire.
 *
 * @param int $term_id Term being saved.
 */
function avanam_ci_save_fields( $term_id ) {
	if ( ! current_user_can( 'manage_product_terms' ) ) {
		return;
	}

	foreach ( avanam_ci_category_fields() as $key => $field ) {
		// phpcs:ignore WordPress.Security.NonceVerification.Missing -- verified by WordPress before this hook.
		if ( ! isset( $_POST[ $key ] ) ) {
			continue;
		}

		// phpcs:ignore WordPress.Security.NonceVerification.Missing -- as above.
		$raw   = wp_unslash( $_POST[ $key ] );
		$value = ( 'textarea' === $field['type'] ) ? sanitize_textarea_field( $raw ) : sanitize_text_field( $raw );

		if ( '' === $value ) {
			delete_term_meta( $term_id, $key );
		} else {
			update_term_meta( $term_id, $key, $value );
		}
	}
}
add_action( 'created_product_cat', 'avanam_ci_save_fields' );
add_action( 'edited_product_cat', 'avanam_ci_save_fields' );
