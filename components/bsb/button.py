import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button, time
from . import BsbComponent, bsb_ns, CONF_BSB_ID

from esphome.const import (
    CONF_ID,
    CONF_TIME_ID,
)

CONF_FIELD_ID = "field_id"

DEPENDENCIES = ["time"]

BsbDatetimeSyncButton = bsb_ns.class_("BsbDatetimeSyncButton", button.Button, cg.Component)

CONFIG_SCHEMA = cv.All(
    button.button_schema(
        BsbDatetimeSyncButton,
    ).extend(
        {
            cv.GenerateID(CONF_BSB_ID): cv.use_id(BsbComponent),
            cv.Required(CONF_FIELD_ID): cv.positive_int,
            cv.Required(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
        }
    ).extend(cv.COMPONENT_SCHEMA),
)


async def to_code(config):
    component = await cg.get_variable(config[CONF_BSB_ID])
    time_component = await cg.get_variable(config[CONF_TIME_ID])
    var = await button.new_button(config)
    await cg.register_component(var, config)

    cg.add(var.set_field_id(config[CONF_FIELD_ID]))
    cg.add(var.set_bsb_component(component))
    cg.add(var.set_time_component(time_component))
