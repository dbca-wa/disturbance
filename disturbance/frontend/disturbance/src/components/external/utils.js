import api from './api'
import {helpers} from '@/utils/hooks' 

export default {
    fetchProfile: function (){
        return new Promise ((resolve,reject) => {
            fetch(api.profile).then(
                async (response) => {
                    if (!response.ok) {
                        return await response.json().then(err => { throw err });
                    }
                    const data = await response.json();
                    resolve(data);
                }).catch(error => {
                    reject(error);
                });
        });

    },
    fetchProposal: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.proposals,id)).then(
                async (response) => {
                    if (!response.ok) {
                        return await response.json().then(err => { throw err });
                    }
                    const data = await response.json();
                    resolve(data);
                }).catch(error => {
                    reject(error);
                });
            });
    },
    fetchCountries: function (){
        return new Promise ((resolve,reject) => {
            fetch(api.countries).then(
                async (response) => {
                    const data = await response.json();
                    resolve(data);
                }).catch(error => {
                    reject(error);
                });
        });

    },
    fetchOrganisationPermissions: async function(id){
        const response = await fetch(helpers.add_endpoint_json(api.my_organisations, id));
        if (!response.ok) {
            const errorData = await response.json();
            throw errorData;
        }
        return await response.json();
    },
    fetchOrganisation: async function(id) {
        const response = await fetch(helpers.add_endpoint_json(api.organisations, id));
        if (!response.ok) {
            const errorData = await response.json();
            throw errorData;
        }
        return await response.json();
    }
}
