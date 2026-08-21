<?php
/**
 * Archive page header: breadcrumb, title, intro and the four counters.
 *
 * Override in your theme at yourtheme/compound-index/parts/page-header.php
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

$ci_stats = Compound_Index_Template::stats();
$ci_intro = Compound_Index_Template::intro();
?>
<header class="ci-head">

	<?php if ( Compound_Index_Settings::on( 'show_breadcrumb' ) ) : ?>
		<nav class="ci-crumbs" aria-label="<?php esc_attr_e( 'Breadcrumb', 'compound-index' ); ?>">
			<?php
			$ci_trail = Compound_Index_Template::breadcrumb();
			$ci_last  = count( $ci_trail ) - 1;
			foreach ( $ci_trail as $ci_i => $ci_crumb ) :
				if ( $ci_crumb['url'] && $ci_i < $ci_last ) :
					?>
					<a href="<?php echo esc_url( $ci_crumb['url'] ); ?>"><?php echo esc_html( $ci_crumb['label'] ); ?></a>
					<span class="ci-crumbs__sep" aria-hidden="true">/</span>
					<?php
				else :
					?>
					<span aria-current="page"><?php echo esc_html( $ci_crumb['label'] ); ?></span>
					<?php
				endif;
			endforeach;
			?>
		</nav>
	<?php endif; ?>

	<h1 class="ci-head__title"><?php echo esc_html( Compound_Index_Template::title() ); ?></h1>

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
