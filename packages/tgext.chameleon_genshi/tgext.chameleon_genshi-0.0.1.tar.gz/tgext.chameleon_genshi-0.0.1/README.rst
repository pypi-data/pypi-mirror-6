tgext.chameleon_genshi
======================

Chameleon Genshi rendering engine support for TG2.3.2+

Usage
------------

Insire your ``config/app_cfg.py`` register the ChameleonGenshi renderer::

    from tgext.chameleon_genshi import ChameleonGenshiRenderer
    
    base_config.register_rendering_engine(ChameleonGenshiRenderer)
    base_config.renderers.append('chameleon_genshi')

