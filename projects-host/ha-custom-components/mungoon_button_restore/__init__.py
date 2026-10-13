"""Restore button changes without overriding a newer Home Assistant command."""
import logging
import voluptuous as vol
from homeassistant.core import State, SupportsResponse, callback
from homeassistant.const import EVENT_CALL_SERVICE
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er, device_registry as dr, area_registry as ar
from homeassistant.helpers.state import async_reproduce_state
from .policy import SnapshotPolicy, affected, DOMAINS, CONTROL_SERVICES

DOMAIN='mungoon_button_restore'
_LOGGER=logging.getLogger(__name__)
KEY=vol.All(cv.string,vol.Match(r'^[a-f0-9]{64}$'))

async def async_setup_entry(hass,entry):
    policy=SnapshotPolicy();entities=er.async_get(hass);devices=dr.async_get(hass);areas=ar.async_get(hass)
    def registry():
        e={k:{'device_id':v.device_id,'area_id':v.area_id,'labels':list(v.labels)} for k,v in entities.entities.items()}
        d={v.id:{'area_id':v.area_id,'labels':list(v.labels)} for v in devices.devices}
        a={k:{'floor_id':v.floor_id,'labels':list(v.labels)} for k,v in areas.areas.items()}
        return e,d,a

    @callback
    def command(event):
        if not policy.sessions:return
        data=event.data;domain=data.get('domain');service=data.get('service');payload=data.get('service_data',{})
        if domain not in DOMAINS|{'homeassistant','scene'}:return
        if domain!='scene' and service not in CONTROL_SERVICES:return
        e,d,a=registry();states={s.entity_id:{'attributes':dict(s.attributes)} for s in hass.states.async_all()}
        targets=affected(domain,service,payload,e,d,a,states)
        policy.command(targets,event.context.id,{k:v.get('device_id') for k,v in e.items()})

    async def capture(call):
        ids=list(dict.fromkeys(call.data['entity_id']));states={}
        for eid in ids:
            s=hass.states.get(eid)
            states[eid]={'state':s.state if s else None,'attributes':dict(s.attributes) if s else {}}
        e,_,_=registry()
        try:policy.capture(call.data['key'],states,call.context.id,{k:v.get('device_id') for k,v in e.items()})
        except ValueError as error:raise ServiceValidationError(str(error)) from error
        return {'captured':ids}

    async def restore(call):
        key=call.data['key'];session=policy.begin_restore(key,call.context.id)
        if not session:return {'restored':[],'skipped':[],'reason':'No active snapshot'}
        restored=[];skipped=[]
        try:
            for eid,saved in session['states'].items():
                current=hass.states.get(eid)
                if eid in session['invalid'] or current is None or current.state in ('unknown','unavailable'):
                    skipped.append(eid);continue
                try:
                    await async_reproduce_state(hass,[State(eid,saved['state'],saved['attributes'])],context=call.context)
                    restored.append(eid)
                except Exception:
                    _LOGGER.exception('Could not restore %s',eid);skipped.append(eid)
        finally:policy.finish(key,session)
        return {'restored':restored,'skipped':skipped}

    async def clear(call):policy.sessions.pop(call.data['key'],None)
    hass.services.async_register(DOMAIN,'capture',capture,schema=vol.Schema({vol.Required('key'):KEY,vol.Required('entity_id'):cv.entity_ids}),supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN,'restore',restore,schema=vol.Schema({vol.Required('key'):KEY}),supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN,'clear',clear,schema=vol.Schema({vol.Required('key'):KEY}))
    entry.async_on_unload(hass.bus.async_listen(EVENT_CALL_SERVICE,command))
    entry.async_on_unload(hass.bus.async_listen('scene_reloaded',lambda event:policy.sessions.clear()))
    hass.data[DOMAIN]=policy
    return True

async def async_unload_entry(hass,entry):
    for service in ('capture','restore','clear'):hass.services.async_remove(DOMAIN,service)
    hass.data.pop(DOMAIN,None)
    return True
