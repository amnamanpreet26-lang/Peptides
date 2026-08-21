<?php
/**
 * Shown when the archive query returns nothing.
 *
 * Override in your theme at yourtheme/compound-index/parts/empty.php
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;
?>
<div class="ci-empty">
	<p class="ci-empty__title"><?php esc_html_e( 'Nothing matches yet.', 'compound-index' ); ?></p>
	<p class="ci-empty__text"><?php esc_html_e( 'Try a different search term, or clear the filters to see the full index.', 'compound-index' ); ?></p>
	<a class="ci-btn" href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>">
		<?php esc_html_e( 'Clear filters', 'compound-index' ); ?>
		<span class="ci-btn__arrow" aria-hidden="true">&rarr;</span>
	</a>
</div>
