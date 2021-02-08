# Just an extract Hopefully it's readable.
   
   def pod_value_destinations(self, app_name='Learn to Code',
                               app_address='learn-to-code'):
        """ if we found a value block get a list of destinations
            and rebase the calc to make sure it adds up to 100 %"""
        if not self.v4v.get('result'):
            self.v4v = self.pod_value_block
        if self.v4v.get('result'):
            hive_server_acc = current_app.config['HIVE_SERVER_ACCOUNT']
            entries = self.v4v['value']['podcast:valueRecipient']
            addresses = []
            names = []
            roles = []
            splits = []
            # TODO #4:
            # Needs error catching code for bad blocks
            # needs to be base role handling on Json file
            # not hard coding
            for entry in entries:
                if entry['@role'] == 'gateway':
                    addresses.append(hive_server_acc)
                    names.append(hive_server_acc)
                    roles.append('gateway')
                elif entry['@role'] == 'index':
                    addresses.append('podcastindex')
                    names.append('PodcastIndex.org')
                    roles.append('index')
                elif entry['@role'] == 'app':
                    addresses.append(app_address)
                    names.append(app_name)
                    roles.append('app')
                else:
                    names.append(entry.get('@name'))
                    addresses.append(entry['@address'])
                    roles.append(entry.get('@role'))
                splits.append(float(entry['@split']))

            splits = self.rebase_splits(splits)
            # Now we'll re-write the value for value block

            if 'gateway' not in roles:
                addresses.append(hive_server_acc)
                names.append(hive_server_acc)
                roles.append('gateway')
                splits.append(1.3)
            if 'app' not in roles:
                #TODO: #5 needs to get the calling app from the API call
                addresses.append(app_address)
                names.append(app_name)
                roles.append('app')
                splits.append(1.3)
            if 'index' not in roles:
                addresses.append('podcastindex')
                names.append('PodcastIndex.org')
                roles.append('index')
                splits.append(1.3)

            splits = self.rebase_splits(splits)
            self.v4v_mod['result'] = True
            self.v4v_mod['recipients'] = []
            for role, name, address, split in zip(roles, names,addresses,splits):
                self.v4v_mod['recipients'].append(
                    {
                        'role' : role,
                        'name' : name,
                        'address': address,
                        'split': split
                    })
            self.v4v_mod.update( {
                'roles' : roles,
                'names' : names,
                'addresses' : addresses,
                'splits' : splits
            })
        return self.v4v_mod

    def v4v_custom_json(self, amount, value_type, sender, ep_data):
        """ Return the bare minimum json with splits and accounts """
        if not self.v4v_mod.get('result'):
            self.pod_value_destinations()
        pay_out = {}
        pay_out['sender'] = sender
        pay_out['episodedata'] = ep_data
        pay_block = []
        for address, split in zip(self.v4v_mod['addresses'],self.v4v_mod['splits']):
            pay_block.append((address, split*float(amount)/100, value_type))
        pay_out['pay_block'] = pay_block
        return pay_out


    def rebase_splits(self, splits, reserve = 3):
        """ Takes in a list of percentages and makes sure they add up
            to 100. Reserve is percentage to hold back for this service
            PodcastIndex and the listening app. (1% each) """
        total = sum(splits)
        if total == 100.0:
            return splits
        new_split = []
        for split in splits:
            new_split.append(split/total * 100)

        return new_split
