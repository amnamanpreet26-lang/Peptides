<?php
/**
 * Archive header: breadcrumb, eyebrow, title, intro and counters.
 *
 * Every value comes from the current product category's fields, falling back to
 * Products - Compound Index.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

$ci_eyebrow = avanam_ci_header_value( 'eyebrow' );
$ci_intro   = avanam_ci_intro();
$ci_stats   = avanam_ci_stats();
$ci_trail   = avanam_ci_breadcrumb();
$ci_last    = count( $ci_trail ) - 1;
?>
<header class="ci-head">

	<nav class="ci-crumbs" aria-label="<?php esc_attr_e( 'Breadcrumb', 'avanam' ); ?>">
		<?php foreach ( $ci_trail as $ci_i => $ci_crumb ) : ?>
			<?php if ( $ci_crumb['url'] && $ci_i < $ci_last ) : ?>
				<a href="<?php echo esc_url( $ci_crumb['url'] ); ?>"><?php echo esc_html( $ci_crumb['label'] ); ?></a>
				<span class="ci-crumbs__sep" aria-hidden="true">/</span>
			<?php else : ?>
				<span aria-current="page"><?php echo esc_html( $ci_crumb['label'] ); ?></span>
			<?php endif; ?>
		<?php endforeach; ?>
	</nav>

	<?php if ( $ci_eyebrow ) : ?>
		<p class="ci-head__eyebrow"><?php echo esc_html( avanam_ci_tokens( $ci_eyebrow ) ); ?></p>
	<?php endif; ?>

	<h1 class="ci-head__title"><?php echo esc_html( avanam_ci_title() ); ?></h1>

	<?php if ( $ci_intro ) : ?>
		<div class="ci-head__intro"><?php echo wp_kses_post( wpautop( $ci_intro ) ); ?></div>
	<?php endif; ?>

	<?php if ( $ci_stats ) : ?>
		<dl class="ci-stats">
			<?php foreach ( $ci_stats as $ci_stat ) : ?>
				<div class="ci-stat">
					<dd class="ci-stat__value"><?php echo esc_html( $ci_stat['value'] ); ?></dd>
					<dt class="ci-stat__label"><?php echo esc_html( $ci_stat['label'] ); ?></dt>
				</div>
			<?php endforeach; ?>
		</dl>
	<?php endif; ?>

</header>
