"""Previous-state snapshots with later-command priority; no HA dependencies."""
from copy import deepcopy

DOMAINS = {'light','switch','input_boolean','cover','fan','humidifier','climate','number','select'}
CONTROL_SERVICES = {
    'turn_on','turn_off','toggle','open_cover','close_cover','stop_cover',
    'set_cover_position','open_cover_tilt','close_cover_tilt','stop_cover_tilt','set_cover_tilt_position',
    'set_percentage','set_preset_mode','oscillate','set_direction','increase_speed','decrease_speed',
    'set_humidity','set_mode','set_temperature','set_hvac_mode','set_fan_mode','set_swing_mode',
    'set_swing_horizontal_mode','set_aux_heat','set_value','select_option','select_first','select_last',
    'select_next','select_previous',
}

def values(value):
    if isinstance(value,str):return {v.strip() for v in value.split(',') if v.strip()}
    return {v for v in value if isinstance(v,str)} if isinstance(value,(list,tuple,set)) else set()

def affected(domain,service,data,entities,devices,areas,states):
    """Resolve entity/group/device/area/floor/label selectors without changing them."""
    if domain=='scene':
        if service=='apply':return set(data.get('entities',{}))
        if service!='turn_on':return set()
    elif domain not in DOMAINS|{'homeassistant'} or service not in CONTROL_SERVICES:return set()
    ids=values(data.get('entity_id'));selected=set()
    device_ids=values(data.get('device_id'));area_ids=values(data.get('area_id'))
    floor_ids=values(data.get('floor_id'));labels=values(data.get('label_id'))
    for eid in set(entities)|set(states):
        entity=entities.get(eid,{});device=devices.get(entity.get('device_id'),{})
        area=entity.get('area_id') or device.get('area_id')
        if (eid in ids or 'all' in ids or entity.get('device_id') in device_ids or area in area_ids
            or areas.get(area,{}).get('floor_id') in floor_ids
            or labels.intersection(entity.get('labels',[]) or []) or labels.intersection(device.get('labels',[]) or [])
            or labels.intersection(areas.get(area,{}).get('labels',[]) or [])):
            selected.add(eid)
    # Service domain restricts broad selectors before physical-device aliases expand.
    if domain!='homeassistant':selected={e for e in selected if e.split('.')[0] in (domain,'group')}
    pending=list(selected);seen=set()
    while pending:
        eid=pending.pop()
        if eid in seen:continue
        seen.add(eid)
        members=values(states.get(eid,{}).get('attributes',{}).get('entity_id'))
        pending.extend(members-seen)
    return seen

class SnapshotPolicy:
    def __init__(self):self.sessions={}

    def capture(self,key,states,context_id,devices):
        if not context_id:raise ValueError('The button run has no HA context.')
        if not 1<=len(states)<=100:raise ValueError('Choose one to 100 devices.')
        if any(e.split('.')[0] not in DOMAINS or s.get('state') in (None,'unknown','unavailable') for e,s in states.items()):
            self.sessions.pop(key,None)
            raise ValueError('All affected devices must be available before this sequence can start.')
        if key not in self.sessions and len(self.sessions)>=200:raise ValueError('Too many active button snapshots.')
        self.sessions[key]={'states':deepcopy(states),'contexts':{context_id},'invalid':set(),
            'devices':dict(devices),'restoring':False}

    def command(self,targets,context_id,devices):
        target_devices={devices[e] for e in targets if devices.get(e)}
        for session in self.sessions.values():
            if context_id and context_id in session['contexts']:continue
            for eid in session['states']:
                if eid in targets or session['devices'].get(eid) in target_devices:session['invalid'].add(eid)

    def begin_restore(self,key,context_id):
        session=self.sessions.get(key)
        if not session or session['restoring']:return None
        session['restoring']=True;session['contexts'].add(context_id)
        return session

    def finish(self,key,session):
        if self.sessions.get(key) is session:self.sessions.pop(key,None)
