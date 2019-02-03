import bpy


class bKeymap():
    def __init__(self, kmi):
        self.kmi = kmi
        self.idname = kmi.idname
        self.type = kmi.type
        self.value = kmi.value
        self.map_type = kmi.map_type

        self.alt = kmi.alt
        self.any = kmi.any
        self.ctrl = kmi.ctrl
        self.shift = kmi.shift
        self.oskey = kmi.oskey
        self.key_modifier = kmi.key_modifier
        self.properties = kmi.properties

        self.idname = kmi.idname

    def to_string(self):
        string = ''
        if self.any:
            string += "Any "
        if self.ctrl:
            string += "Ctrl "
        if self.alt:
            string += "Alt "
        if self.shift:
            string += "Shift "
        if self.oskey:
            string += "OsKey "
        if self.key_modifier != 'NONE':
            string += self.key_modifier + " "
        if self.type != "NONE":
            string += self.type
        return string


class bProp():
    def __init__(self, prop):

        for p in prop:
            setattr(self, p[0], p[1])


class KeymapManager():
    keymap_List = {"new": [],
                   "replaced": []}

    def __init__(self):

        # Define global variables
        self.wm = bpy.context.window_manager
        self.kca = self.wm.keyconfigs.addon
        self.kcu = self.wm.keyconfigs.user

        self.km = None
        self.ukmis = None
        self.akmis = None

    # Decorators

    def replace_km_dec(func):
        def func_wrapper(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):

            new_kmi = func(self, idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier, properties=properties)

            keymlap_List = {'km': self.km, 'kmis': self.ukmis, 'new_kmi': new_kmi}
            duplicates = [k for k in self.ukmis if k.idname == idname]

            if len(duplicates):
                for k in duplicates:
                    if self.tool_compare(new_kmi, k):
                        # TODO if multiple keymap is assigned to the same command, how to replace the proper one ?
                        print("{} : '{}' tool found, replace keymap '{}' to '{}'".format(self.km.name, k.idname, k.to_string(), new_kmi.to_string()))

                        k_old = bKeymap(k)

                        keymlap_List['old_kmi'] = k_old
                        keymlap_List['old_kmi_id'] = k.id

                        # Replace keymap attribute
                        self.kmi_replace(new_kmi, k)

                        # Store keymap in class variable
                        self.keymap_List["replaced"].append(keymlap_List)

                        return k

                return new_kmi
        return func_wrapper

    # Functions

    def kmi_replace(self, km_src, km_dest):
        km_dest.key_modifier = km_src.key_modifier
        km_dest.map_type = km_src.map_type
        km_dest.type = km_src.type
        km_dest.value = km_src.value

        if km_src.any != km_dest.any:
            km_dest.any = km_src.any
        km_dest.alt = km_src.alt
        km_dest.ctrl = km_src.ctrl
        km_dest.shift = km_src.shift
        km_dest.oskey = km_src.oskey

    def kmi_compare(self, kmi1, kmi2):
        return kmi1.type == kmi2.type and kmi1.ctrl == kmi2.ctrl and kmi1.alt == kmi2.alt and kmi1.shift == kmi2.shift and kmi1.any == kmi2.any and kmi1.oskey == kmi2.oskey and kmi1.key_modifier == kmi2.key_modifier and kmi1.map_type == kmi2.map_type and kmi1.value == kmi2.value

    def tool_compare(self, kmi1, kmi2):
        kmi1_props = self.kmi_prop_list(kmi1.properties)
        kmi2_props = self.kmi_prop_list(kmi2.properties)

        if len(kmi1_props) != len(kmi2_props):
            return False
        else:
            for i in range(len(kmi1_props)):
                if kmi1_props[i] != kmi2_props[i]:
                    return False
                else:
                    prop1 = self.kmi_prop_getattr(kmi1.properties, kmi1_props[i])
                    prop2 = self.kmi_prop_getattr(kmi2.properties, kmi2_props[i])

                    if prop1 != prop2:
                        return False
            else:
                return True

    def prop_compare(self, prop1, prop2, compare_size=False):
        if prop2 is None:
            return None
        else:
            kmi1_props = self.kmi_prop_list(prop1)
            kmi2_props = self.kmi_prop_list(prop2)

            if compare_size:
                if len(kmi1_props) != len(kmi2_props):
                    return False
                else:
                    for i in range(len(kmi1_props)):
                        if kmi1_props[i] != kmi2_props[i]:
                            return False
                        else:
                            p1 = self.kmi_prop_getattr(prop1, kmi1_props[i])
                            p2 = self.kmi_prop_getattr(prop2, kmi2_props[i])

                            if p1 != p2:
                                return False
                    else:
                        return True
            else:
                for p2name in kmi2_props:
                    if p2name in kmi1_props:
                        p1 = self.kmi_prop_getattr(prop1, p2name)
                        p2 = self.kmi_prop_getattr(prop2, p2name)
                        if p1 != p2:
                            return False
                else:
                    return True

    @replace_km_dec
    def kmi_set_replace(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):
        kmi = self.kmi_set(idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier, properties=properties)
        return kmi

    def kmi_set(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):
        kmi = self.km.keymap_items.new(idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier)
        kmi.active = True
        for p in properties:
            self.kmi_prop_setattr(kmi.properties, p[0], p[1])
        print("{} : assigning new tool '{}' to keymap '{}'".format(self.km.name, kmi.idname, kmi.to_string()))

        # Store keymap in class variable
        self.keymap_List["new"].append((self.km, kmi))

        return kmi

    def kmi_find(self, idname=None, type=None, value=None, alt=None, any=None, ctrl=None, shift=None, oskey=None, key_modifier=None, properties=None):
        def attr_compare(src_attr, comp_attr):
            if comp_attr is not None:
                if comp_attr != src_attr:
                    return False
                else:
                    return True
            else:
                return None

        for k in self.ukmis:
            if attr_compare(k.idname, idname) is False:
                continue

            if attr_compare(k.type, type) is False:
                continue

            if attr_compare(k.value, value) is False:
                continue

            if attr_compare(k.alt, alt) is False:
                continue

            if attr_compare(k.any, any) is False:
                continue

            if attr_compare(k.ctrl, ctrl) is False:
                continue

            if attr_compare(k.shift, shift) is False:
                continue

            if attr_compare(k.oskey, oskey) is False:
                continue

            if attr_compare(k.key_modifier, key_modifier) is False:
                continue

            if self.prop_compare(k.properties, properties) is False:
                continue

            return k

        else:
            return None

    def kmi_init(self, name, space_type='EMPTY', region_type='WINDOW', modal=False, tool=False):
        self.ukmis = self.kcu.keymaps[name].keymap_items
        self.km = self.kcu.keymaps.new(name, space_type=space_type, region_type=region_type, modal=modal, tool=tool)
        self.akmis = self.kcu.keymaps[name].keymap_items

    def kmi_prop_setattr(self, kmi_props, attr, value):
        try:
            setattr(kmi_props, attr, value)
        except AttributeError:
            print("Warning: property '%s' not found in keymap item '%s'" %
                  (attr, kmi_props.__class__.__name__))
        except Exception as e:
            print("Warning: %r" % e)

    def kmi_prop_getattr(self, kmi_props, attr):
        try:
            return getattr(kmi_props, attr)
        except AttributeError:
            print("Warning: property '%s' not found in keymap item '%s'" % (attr, kmi_props.__class__.__name__))
        except Exception as e:
            print("Warning: %r" % e)

    def kmi_prop_list(self, kmi_props):
        prop = dir(kmi_props)[3:]
        skip = ['path', 'constraint_axis']
        for s in skip:
            if s in prop:
                prop.remove(s)
        return prop

    def kmi_set_active(self, enable, idname=None, type=None, value=None, alt=None, any=None, ctrl=None, shift=None, oskey=None, key_modifier=None, properties=None):
        kmi = self.kmi_find(idname=idname, type=type, value=value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier, properties=properties)
        if kmi:
            kmi.active = enable
            return enable

        return None