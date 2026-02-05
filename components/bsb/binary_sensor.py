import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from . import BsbComponent, bsb_ns, CONF_BSB_ID, CONF_PARAMETER_NUMBER, CONF_BSB_TYPE

from esphome.const import (
    CONF_UPDATE_INTERVAL
)

CONF_FIELD_ID = "field_id"
CONF_ENABLE_BYTE = "enable_byte"

BsbBinarySensor = bsb_ns.class_("BsbBinarySensor", binary_sensor.BinarySensor)

CONFIG_SCHEMA = cv.All(
    binary_sensor.binary_sensor_schema(
        BsbBinarySensor,
    ).extend(
        {
            cv.GenerateID(CONF_BSB_ID): cv.use_id(BsbComponent),
            cv.Required(CONF_FIELD_ID): cv.positive_int,
            cv.Optional(CONF_ENABLE_BYTE, default="1"): cv.one_of(0x00, 0x01, 0x06, int=True),
            cv.Optional(CONF_PARAMETER_NUMBER, default="0"): cv.positive_int,
            cv.Optional(CONF_UPDATE_INTERVAL, default="15min"): cv.update_interval,
        }
    ),
    cv.has_exactly_one_key(CONF_FIELD_ID),
)


async def to_code(config):
    component = await cg.get_variable(config[CONF_BSB_ID])
    var = await binary_sensor.new_binary_sensor(config)

    if CONF_FIELD_ID in config:
        cg.add(var.set_field_id(config[CONF_FIELD_ID]))

    if CONF_ENABLE_BYTE in config:
        cg.add(var.set_enable_byte(config[CONF_ENABLE_BYTE]))

    if CONF_UPDATE_INTERVAL in config:
        cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))

    cg.add(component.register_sensor(var))
    cg.add(var.set_retry_interval(component.get_retry_interval()))
    cg.add(var.set_retry_count(component.get_retry_count()))
