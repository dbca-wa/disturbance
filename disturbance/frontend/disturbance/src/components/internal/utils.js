import api from './api'
import {helpers} from '@/utils/hooks' 

export default {
    fetchProposal: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.proposals,id)).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    let data = await response.json();
                    resolve(data);
                }).catch((error) => {
                    reject(error);
                }
            );
        });
    },
    fetchOrganisations: function(){
        return new Promise ((resolve,reject) => {
            fetch(api.organisations).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    let data = await response.json();
                    resolve(data);
                }).catch((error) => {
                    reject(error);
                }
            );
        });
    },
    fetchCountries: function (){
        return new Promise ((resolve,reject) => {
            fetch(api.countries).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    let data = await response.json();
                    resolve(data);
                }).catch((error) => {
                    reject(error);
                }
            );
        });

    },
    fetchOrganisation: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.organisations,id)).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    let data = await response.json();
                    resolve(data);
                }).catch((error) => {
                    reject(error);
                }
            );
        });
    },
}
