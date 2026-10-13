import copy,importlib.util,unittest
from pathlib import Path
path=Path(__file__).parent/'ha-custom-components/mungoon_button_restore/policy.py'
spec=importlib.util.spec_from_file_location('restore_policy',path);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PriorityTests(unittest.TestCase):
 def setUp(self):
  self.policy=p.SnapshotPolicy();self.states={'switch.lamp':{'state':'on','attributes':{}},'humidifier.arete':{'state':'on','attributes':{'humidity':50}},'cover.curtain':{'state':'open','attributes':{'current_position':80}}}
  self.devices={'switch.lamp':'lamp','humidifier.arete':'arete','fan.arete':'arete','cover.curtain':'curtain'}
  self.policy.capture('button',self.states,'button-run',self.devices)
 def test_scheduled_off_even_when_already_off_takes_priority_for_only_that_device(self):
  self.policy.command({'switch.lamp'},'button-run',self.devices)
  self.policy.command({'switch.lamp'},'schedule-run',self.devices)
  s=self.policy.begin_restore('button','double-run');self.assertEqual(s['invalid'],{'switch.lamp'});self.assertEqual(len(s['states']),3)
  self.policy.command({'humidifier.arete'},'double-run',self.devices);self.assertEqual(s['invalid'],{'switch.lamp'})
 def test_return_to_same_visible_state_still_does_not_erase_later_intent(self):
  for context in ('automation-off','automation-on'):self.policy.command({'switch.lamp'},context,self.devices)
  self.assertIn('switch.lamp',self.policy.sessions['button']['invalid'])
 def test_automation_started_by_button_has_its_own_priority(self):
  self.policy.command({'switch.lamp'},'child-automation-context',self.devices)
  self.assertIn('switch.lamp',self.policy.sessions['button']['invalid'])
 def test_manual_ha_commands_and_other_control_of_same_device_are_respected(self):
  self.policy.command({'fan.arete'},'manual-ha-user',self.devices)
  self.assertEqual(self.policy.sessions['button']['invalid'],{'humidifier.arete'})
 def test_multi_button_and_once_only_snapshots(self):
  self.policy.capture('another',self.states,'another-button',self.devices)
  self.policy.command({'switch.lamp'},'another-button',self.devices)
  self.assertIn('switch.lamp',self.policy.sessions['button']['invalid']);self.assertFalse(self.policy.sessions['another']['invalid'])
  session=self.policy.begin_restore('button','restore');self.assertIsNone(self.policy.begin_restore('button','second'));self.policy.finish('button',session);self.assertIsNone(self.policy.begin_restore('button','third'))
 def test_recapture_replaces_snapshot_and_offline_capture_clears_old_state(self):
  self.policy.command({'switch.lamp'},'other',self.devices);self.policy.capture('button',self.states,'new',self.devices);self.assertFalse(self.policy.sessions['button']['invalid'])
  states=copy.deepcopy(self.states);states['switch.lamp']['state']='unavailable'
  with self.assertRaises(ValueError):self.policy.capture('button',states,'new',self.devices)
  self.assertNotIn('button',self.policy.sessions)
 def test_new_command_during_restore_invalidates_a_remaining_target(self):
  s=self.policy.begin_restore('button','double');self.policy.command({'humidifier.arete'},'schedule',self.devices);self.assertIn('humidifier.arete',s['invalid'])
 def test_room_device_floor_labels_groups_and_presets(self):
  entities={'switch.lamp':{'device_id':'lamp'},'humidifier.arete':{'device_id':'arete','area_id':'bath','labels':['dry']},'scene.tv':{},'group.den':{}}
  devices={'lamp':{'area_id':'den'},'arete':{'area_id':'den'}};areas={'den':{'floor_id':'first','labels':['living']},'bath':{'floor_id':'first'}}
  states={'scene.tv':{'attributes':{'entity_id':['switch.lamp','humidifier.arete']}},'group.den':{'attributes':{'entity_id':['switch.lamp']}}}
  def resolve(domain,service,data):return p.affected(domain,service,data,entities,devices,areas,states)
  self.assertEqual(resolve('switch','turn_off',{'area_id':'den'}),{'switch.lamp'})
  self.assertEqual(resolve('humidifier','turn_off',{'device_id':'arete'}),{'humidifier.arete'})
  self.assertEqual(resolve('homeassistant','turn_off',{'floor_id':'first'}),{'switch.lamp','humidifier.arete'})
  self.assertEqual(resolve('homeassistant','turn_off',{'label_id':'dry'}),{'humidifier.arete'})
  self.assertEqual(resolve('switch','turn_off',{'label_id':'living'}),{'switch.lamp'})
  self.assertIn('switch.lamp',resolve('homeassistant','turn_off',{'entity_id':'group.den'}))
  self.assertTrue({'switch.lamp','humidifier.arete'}<=resolve('scene','turn_on',{'entity_id':'scene.tv'}))
  self.assertEqual(resolve('scene','apply',{'entities':{'switch.lamp':'off'}}),{'switch.lamp'})
  self.assertEqual(resolve('scene','create',{'entity_id':'scene.tv'}),set())
  self.assertEqual(resolve('homeassistant','update_entity',{'entity_id':'switch.lamp'}),set())
  self.assertEqual(resolve('switch','turn_off',{'entity_id':'all'}),{'switch.lamp','group.den'})

if __name__=='__main__':unittest.main()
