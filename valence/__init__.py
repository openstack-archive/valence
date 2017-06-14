import coloredlogs
import valence.conf

CONF = valence.conf.CONF

coloredlogs.install(level=(CONF.api.log_level).upper(),
                    field_styles=CONF.api.field_styles,
                    fmt=CONF.api.log_format,
                    level_styles=CONF.api.level_styles)
