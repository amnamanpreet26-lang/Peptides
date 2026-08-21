<?php
/**
 * Shown when the archive query returns nothing.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;
?>
<div class="ci-empty">
	<p class="ci-empty__title"><?php esc_html_e( 'Nothing matches yet.', 'avanam' ); ?></p>
	<p class="ci-empty__text"><?php esc_html_e( 'Try a different search term, or clear the filters to see the full index.', 'avanam' ); ?></p>
	<a class="ci-btn" href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>">
		<?php esc_html_e( 'Clear filters', 'avanam' ); ?>
		<span class="ci-btn__arrow" aria-hidden="true">&rarr;</span>
	</a>
</div>
