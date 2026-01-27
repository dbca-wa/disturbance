import Section from '../components/forms/section.vue'
import Group from '../components/forms/group.vue'
import Radio from '../components/forms/radio.vue'
import Conditions from '../components/forms/conditions.vue'
import SelectConditions from '../components/forms/select-conditions.vue'
import Checkbox from '../components/forms/checkbox.vue'
import File from '../components/forms/file.vue'
import Select from '../components/forms/select.vue'
import DateField from '../components/forms/date-field.vue'
import TextField from '../components/forms/text.vue'
import TextArea from '../components/forms/text-area.vue'
import Label from '../components/forms/label.vue'
import TextInfo from '../components/forms/text_info.vue'
import AssessorText from '../components/forms/readonly_text.vue'
import HelpText from '../components/forms/help_text.vue'
import HelpTextUrl from '../components/forms/help_text_url.vue'
import CommentRadioCheckBox from '../components/forms/comment_icon_checkbox_radio.vue'
import IFrame from '../components/forms/iframe.vue'
import LayerInfo from '../components/forms/layer_info.vue'
import RefreshRadio from '../components/forms/refresh_radio.vue'
import {api_endpoints} from "@/utils/hooks.js"

export default{
    name: 'DASRenderer',
    renderChildren(h,c,data=null,assessorData=null) {
        var is_readonly = this.status_data.readonly;
        var assessorStatus = this.status_data.assessorStatus;
        // var assessorData = this.status_data.assessorData;
        var commentData = this.status_data.commentData;
        var layerData= this.status_data.layerData;
        var assessorInfo = this.status_data.assessorInfo;
        var proposalId = this.status_data.proposalId;
        var proposalLodgementDate = this.status_data.proposalLodgementDate;
        var assessorMode = false;
        var assessorCanAssess = false;
        var assessorLevel = '';
        var readonly = false;
        var _elements = [];
        var comment_boxes=[];
        var help_text = '';
        var help_text_assessor = '';
        var help_text_url = '';
        var help_text_assessor_url
        var addInfoApplicant= this.status_data.addInfoApplicant
        var addInfoAssessor= this.status_data.addInfoAssessor
        var historyAddInfoAssessor= this.status_data.historyAddInfoAssessor
        var refreshTimeStamp= this.status_data.refreshTimeStamp
        if (assessorStatus != null){
            assessorMode = assessorStatus['assessor_mode'];
            assessorCanAssess = assessorStatus['has_assessor_mode'];
            assessorLevel = assessorStatus['assessor_level'];
        }
        //var site_url = api_endpoints.site_url;
        var site_url = (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/");

        // Visibility
        var visibility = this.getVisibility(h,c,is_readonly,assessorMode,assessorCanAssess)
        if (!visibility.visible){ return "" }
        var assessor_visibility = assessorLevel == 'assessor' && this.status_data.assessorStatus.has_assessor_mode? true : false;
        assessor_visibility = !assessor_visibility;

        // Editablility
        // readonly = !visibility.editable;
        // var orig_readonly = !visibility.editable
        var orig_readonly = (this.status_data.has_prefilled_once)? !visibility.editable : true;

        var val = (data) ? (data[c.name]) ? data[c.name] : null : null;
        var layer_val = (layerData) ? layerData.find(at => at.name == c.name) : null;
        //Make components answered by SQS readonly
        readonly = (layer_val) ? true : orig_readonly;
        var refresh_timestamp = (refreshTimeStamp) ? (refreshTimeStamp[c.name]) ? refreshTimeStamp[c.name] : null : null;
        //console.log(layerData);
        //var comment_val = (commentData) ? (commentData[c.name]) ? commentData[c.name] : null : null;
        var add_info_applicant_val = (addInfoApplicant) ? (addInfoApplicant[c.name]) ? addInfoApplicant[c.name] : null : null;
        var add_info_assessor_val = (addInfoAssessor) ? (addInfoAssessor[c.name]) ? addInfoAssessor[c.name] : null : null;
        var history_info_assessor_val = (historyAddInfoAssessor) ? (historyAddInfoAssessor[c.name]) ? historyAddInfoAssessor[c.name] : null : null;
        var comment_val= null;
	    var show_add_info_proponent = true;
        if(layer_val){
  	    try {
	        show_add_info_proponent = layer_val.sqs_data.other_data.show_add_info_section_prop
            // show_add_info_proponent = layer_val.sqs_data && layer_val.sqs_data.other_data && layer_val.sqs_data.other_data.show_add_info_section_prop ? layer_val.sqs_data.other_data.show_add_info_section_prop : true;	
	    } catch (ex) {
            show_add_info_proponent = true;
            console.log(ex);
	    }
        }
        if(commentData){
            if(commentData.constructor != Object){
                    comment_val = commentData.find(at => at.name == c.name)
                }
            else{
                comment_val = (commentData[c.name]) ? commentData[c.name] : null;
            }
        }

        if (c && c.help_text && c.help_text.indexOf("site_url:/") >= 0) {
            help_text = c.help_text.replace('site_url:/', site_url);
            if (help_text.indexOf("anchor=") >= 0) {
                help_text = help_text.replace('anchor=', "#");
            }
        } else {
            help_text = c.help_text;
        }

        if (c && c.help_text_assessor && c.help_text_assessor.indexOf("site_url:/") >= 0) {
            help_text_assessor = c.help_text_assessor.replace('site_url:/', site_url);
            if (help_text_assessor.indexOf("anchor=") >= 0) {
                help_text_assessor = help_text_assessor.replace('anchor=', "#");
            }
        } else {
            help_text_assessor = c.help_text_assessor;
        }

        // repeat for help_text_url
        if (c && c.help_text_url && c.help_text_url.indexOf("site_url:/") >= 0) {
            help_text_url = c.help_text_url.replace('site_url:/', site_url);
            if (help_text_url.indexOf("anchor=") >= 0) {
                help_text_url = help_text_url.replace('anchor=', "#");
            }
        } else {
            help_text_url = c.help_text_url;
        }

        if (c && c.help_text_assessor_url && c.help_text_assessor_url.indexOf("site_url:/") >= 0) {
            help_text_assessor_url = c.help_text_assessor_url.replace('site_url:/', site_url);
            if (help_text_assessor_url.indexOf("anchor=") >= 0) {
                help_text_assessor_url = help_text_assessor_url.replace('anchor=', "#");
            }
        } else {
            help_text_assessor_url = c.help_text_assessor_url;
        }

        if (assessorMode && $.inArray(c.type,['declaration','group','section','label']) == -1){
            comment_boxes = this.generateCommentTextBoxes(h,c,val,assessorLevel,commentData,assessorInfo, comment_val);
            //console.log(c.type,comment_boxes);
        }


        var id = 'id_' + c.name;
        var id1 = id + '_1'
        var id2 = id + '_2'
        var id3 = id + '_3'
        var value = null;

        switch (c.type) {
            case 'text':
        		readonly = (c.readonly) ? (c.readonly): (readonly);
                _elements.push(
                    <TextField type="text" name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} readonly={readonly} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                )
                break;
            case 'text_info':
                _elements.push(
                    <TextInfo label={c.label} name={c.name} value={val} id={id} />
                )
                break;
            case 'iframe':
                _elements.push(
                    <IFrame src={c.src} title={c.title} name={c.name} id={id} width={c.width} height={c.height} frameborder={c.frameborder} scrolling={c.scrolling} marginheight={c.marginheight} marginwidth={c.marginwidth} />
                )
                break;
            case 'number':
                _elements.push(
                    <TextField type="number" name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} readonly={readonly} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                )
                break;
            case 'email':
                _elements.push(
                    <TextField type="email" name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} readonly={readonly} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                )
                break;
            case 'select':
                value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div>
                        <Select readonly={readonly} name={c.name} label={c.label} value={c.value} id={id} comment_value={comment_val} options={c.options} help_text={help_text} help_text_assessor={help_text_assessor} value={val} handleChange={this.selectionChanged}  conditions={c.conditions} assessorMode={assessorMode} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                        <SelectConditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id1} readonly={readonly} isRequired={c.isRequired}/>
                    </div>
                )
                break;
            case 'multi-select':

                // if (assessorMode && $.inArray(c.type,['declaration','group','section','label']) == -1){
                //     var comment_boxes = this.generateCommentTextBoxes(h,c,val,assessorLevel,commentData,assessorInfo, comment_val);
                //     // Merge assessor boxes to _elements array
                //     //Array.prototype.push.apply(_elements,boxes);
                //     console.log(comment_boxes);
                // }
                //console.log(comment_boxes);
                _elements.push(
                    <Select name={c.name} label={c.label} value={val} id={id} comment_value={comment_val} options={c.options} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} handleChange={this.selectionChanged} readonly={readonly} isMultiple={true} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                )
                break;
            case 'text_area':
                _elements.push(
                    <TextArea readonly={readonly} name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} assessorMode={assessorMode} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                )
                break;
            case 'label':
                _elements.push(
                    //<Label value={c.label} id='id_' + {c.name}/>
                    <Label value={c.label} id={id} />
                )
                break;
            case 'radiobuttons':
                value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div class="form-group">
                        <label id={id} class="inline">{c.label}</label>
                            <HelpText help_text={help_text}/>
                            <HelpText help_text={help_text_assessor} assessorMode={assessorMode} isForAssessor={true}/>
                            <HelpTextUrl help_text_url={help_text_url}/>
                            <HelpTextUrl help_text_url={help_text_assessor_url} assessorMode={assessorMode} isForAssessor={true}/>
                            <RefreshRadio parent_name={c.name} parent_label={c.label} assessorMode={assessorMode} layer_data={layer_val} refresh_time_value={refresh_timestamp} proposal_id={proposalId}/>
                            <CommentRadioCheckBox assessor_readonly={assessor_visibility} name={c.name} comment_value={comment_val} assessorMode={assessorMode} label={c.label} comment_boxes={JSON.stringify(comment_boxes)}/>
                            <LayerInfo layer_value={layer_val} assessorMode={true}/>
                            {c.options.map(op =>{
                                return(
                                    <Radio name={c.name} label={op.label} value={op.value} isRequired={op.isRequired} id={id1} savedValue={val} handleChange={this.handleRadioChange} conditions={c.conditions} readonly={readonly}/>
                                )
                            })}
                            <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id2} readonly={readonly}/>
                    </div>
                )
                break;
            case 'group':
                value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                var found=null;
                found=c.children.find(child => child.type == 'checkbox' && ((layerData) ? layerData.find(at => at.name == child.name) : null))
                _elements.push(
                    <Group label={c.label} name={c.name} id={id} help_text={help_text} help_text_url={help_text_url} isRemovable={true} assessorMode={assessorMode} layer_val={found} refresh_time_value={refresh_timestamp} proposal_id={proposalId} >
                        {c.children.map(c=>{
                            return (
                                <div> 
                                    {this.renderChildren(h,c,value)}
                                </div>
                            )
                        })}
                    </Group>
                )
                break;
            case 'section':
                value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                if(!this.sections.map(a=>a.name).includes(c.name))
                {
                    this.sections.push({name:c.name,label:c.label});
                }
                //this.sections.push({name:c.name,label:c.label});
                _elements.push(
                    <Section label={c.label} secKey={c.name} id={c.name}>
                        {c.children.map(d=>{
                            return (
                                <div>
                                    {this.renderChildren(h,d,value)}
                                </div>
                            )
                        })}
                    </Section>
                )
                break;

            case 'checkbox':
                _elements.push(
                    <div class="form-group">
                        <Checkbox group={c.group} name={c.name} label={c.label} id={id1} help_text={help_text} help_text_url={help_text_url} value={val} handleChange={this.handleCheckBoxChange} conditions={c.conditions} readonly={readonly} isRequired={c.isRequired} layer_value={layer_val} assessorMode={assessorMode}/>
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id2} isRequired={c.isRequired}/>
                    </div>
                )
                break;
            case 'declaration':
                value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name] : null ;
                }
                _elements.push(
                    <div class="form-group">
                        <label id={id1}>{c.label}</label>
                        <Checkbox name={c.name} label={c.label} value={val} id={id2} help_text={help_text} help_text_url={help_text_url} handleChange={this.handleCheckBoxChange} conditions={c.conditions} isRequired={c.isRequired}/>
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={value} id={id3} isRequired={c.isRequired}/>
                    </div>
                )
                break;
            case 'file':
                _elements.push(
                    <File name={c.name} label={c.label} value={val} id={id} comment_value={comment_val} isRepeatable={c.isRepeatable} handleChange={this.handleFileChange} readonly={readonly} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} docsUrl={this.status_data.docs_url} assessor_readonly={assessor_visibility} proposal_id={proposalId} proposal_lodgement_date={proposalLodgementDate} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)}/>
                )
                break;
            case 'date':
                _elements.push(
                    <DateField name={c.name} label={c.label} value={val} id={id} comment_value={comment_val}  handleChange={this.handleFileChange} readonly={readonly} help_text={help_text} help_text_assessor={help_text_assessor} assessorMode={assessorMode} assessor_readonly={assessor_visibility} isRequired={c.isRequired} help_text_url={help_text_url} help_text_assessor_url={help_text_assessor_url} comment_boxes={JSON.stringify(comment_boxes)} layer_val={layer_val}/>
                )
                break;
            default:
            return "";
        }
        if (assessorMode && $.inArray(c.type,['declaration','group','section','label']) == -1 && c.canBeEditedByAssessor){
            var boxes = this.generateAssessorTextBoxes(h,c,val,assessorLevel,assessorData,assessorInfo);
            // Merge assessor boxes to _elements array
            Array.prototype.push.apply(_elements,boxes);
        }
        if (layer_val && show_add_info_proponent && $.inArray(c.type,['declaration','group','section','label', 'checkbox']) == -1){
            var applicant_boxes = this.generateAddInfoApplicantTextBoxes(h,c,val,assessorLevel,orig_readonly, add_info_applicant_val);
            // Merge assessor boxes to _elements array
            Array.prototype.push.apply(_elements,applicant_boxes);
        }
        if (assessorMode && $.inArray(c.type,['declaration','group','section','label', 'checkbox']) == -1){
            var assessor_boxes = this.generateAddInfoAssessorTextBoxes(h,c,val,assessorLevel, add_info_assessor_val);
            // Merge assessor boxes to _elements array
            Array.prototype.push.apply(_elements,assessor_boxes);
        }
        if (assessorMode && $.inArray(c.type,['declaration','group','section','label', 'checkbox']) == -1){
            var history_assessor_boxes = this.generateHistoryAddInfoAssessorTextBoxes(h,c,val,assessorLevel, history_info_assessor_val);
            // Merge assessor boxes to _elements array
            Array.prototype.push.apply(_elements,history_assessor_boxes);
        }
        
        return _elements;
    },

    handleRadioChange(e){
        var conditions = $(e.target).data('conditions');
        if (conditions && conditions !== undefined) {
            // var cons = Object.keys(conditions);
            var btns = $('input[name='+e.target.name+']');
            $.each(btns,function (i,input) {
                $("#cons_"+e.target.name+'_'+input.value).addClass('d-none');
            });
            $("#cons_"+e.target.name+'_'+e.target.value).removeClass('d-none');
        }
    },
    handleCheckBoxChange(e){
        var conditions = $(e.target).data('conditions');
        if (conditions && conditions !== undefined) {
            // var cons = Object.keys(conditions);
            var btns = $('input[name='+e.target.name+']');
            $.each(btns,function (i,input) {
                $("#cons_"+e.target.name+'_'+input.value).addClass('d-none');

            });
            if(e.target.checked){
                $("#cons_"+e.target.name+'_'+e.target.value).removeClass('d-none');
            }
        }

    },
    handleDeclaration(){
        return true;
    },
    selectionChanged(target){
        var conditions = $(target).data('conditions');

        if (conditions) {
            var cons = Object.keys(conditions);
            for (var i = 0; i < cons.length; i++) {
                if (cons[i] == target.value) {
                    $("#cons_"+target.name+'_'+target.value).removeClass('d-none');
                }else{
                    $("#cons_"+target.name+'_'+cons[i]).addClass('d-none');
                }
            }
        }
    },
    getSections(){
        return this.sections;
    },
    sections:[],
    generateAssessorTextBoxes(h,c,val,assessor_mode,assessor_data,assessor_info){
        var box_visibility = this.status_data.assessorStatus.assessor_box_view
        var boxes = [];
        var assessor_visibility;
        var name = '';
        var referral_name = '';
        var referral_visibility = '';
        var referral_label = '';
        if (!this.status_data.can_user_edit){
            if (assessor_data){
                var _dt = assessor_data.find(at => at.name == c.name)
                // Assessor Data
                var assessor_name = `${c.name}-Assessor`;
                var assessor_val = _dt == undefined || _dt.assessor == '' ? val : _dt.assessor;
                assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                assessor_visibility = !assessor_visibility;
                boxes.push(
                    <AssessorText box_view={box_visibility} type="text" name={assessor_name} value={assessor_val} label={'Assessor (Approved Management Actions)'} help_text={c.help_text} readonly={assessor_visibility}/>
                )
                // Referral Data
                var current_referral_present=false;
                if (_dt != undefined){
                    $.each(_dt.referrals,(i,v)=> {
                        if (v.email == assessor_info.email){ current_referral_present = true; }
                        var readonly = v.email == assessor_info.email && assessor_mode == 'referral' && this.status_data.assessorStatus.assessor_can_assess ? false : true;
                        var referral_name = `${c.name}-Referral-${v.email}`;
                        boxes.push(
                            <AssessorText box_view={box_visibility} type="text" name={referral_name} value={v.value} label={v.full_name + ' (Suggested Management Actions)'} help_text={c.help_text} readonly={readonly}/>
                        )
                    });
                }
                if (assessor_mode == 'referral'){
                    if (!current_referral_present){
                        //console.log('here', current_referral_present)
                        // Add Referral Box
                        referral_name = `${c.name}-Referral-${assessor_info.email}`;
                        referral_visibility =  assessor_mode == 'referral' && this.status_data.assessorStatus.assessor_can_assess ? false : true ;
                        referral_label = `${assessor_info.name}` + ' (Suggested Management Actions)';
                        boxes.push(
                            // <AssessorText box_view={box_visibility} type="text" name={referral_name} value={assessor_val} label={referral_label} readonly={referral_visibility}/>
                            <AssessorText box_view={box_visibility} type="text" name={referral_name} label={referral_label} readonly={referral_visibility}/>
                        )
                    }
                }
            }
            else{
                if (assessor_mode == 'assessor'){
                    name = `${c.name}-Assessor`;
                    assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                    assessor_visibility = !assessor_visibility;
                    boxes.push(
                        <AssessorText box_view={box_visibility} type="text" name={name} value={val} label={'Assessor (Approved Management Actions)'} help_text={c.help_text} readonly={assessor_visibility}/>
                    )
                }
                else if (assessor_mode == 'referral'){
                    // Add Assessor Box
                    name = `${c.name}-Assessor`;
                    assessor_visibility = assessor_mode != 'assessor' ? true : false;
                    boxes.push(
                        <AssessorText box_view={box_visibility} type="text" name={name} value={val} label={'Assessor (Approved Management Actions)'} help_text={c.help_text} readonly={assessor_visibility}/>
                    )
                    // Add Referral Box
                    referral_name = `${c.name}-Referral-${assessor_info.email}`;
                    referral_visibility = assessor_mode != 'referral' ? true : false;
                    referral_label = `${assessor_info.name}` + ' (Suggested Management Actions)';
                    boxes.push(
                        <AssessorText box_view={box_visibility} type="text" name={referral_name} value={val} label={referral_label} readonly={referral_visibility}/>
                    )
                }
            }
        }
        if (boxes.length > 0){
            boxes = [<div class="row"> {boxes} </div>]
        }
        return boxes;
    },
    status_data : {},
    store_status_data(readonly,has_prefilled_once,assessorData,layerData,commentData,addInfoApplicant,addInfoAssessor,historyAddInfoAssessor, refreshTimeStamp,assessorEmail,assessorMode,can_user_edit,docs_url, proposalId, applicationType, proposalLodgementDate){
        this.status_data = {
            'readonly': readonly,
            'has_prefilled_once': has_prefilled_once,
            'assessorData': assessorData,
            'layerData': layerData,
            'commentData': commentData,
            'addInfoApplicant': addInfoApplicant,
            'addInfoAssessor': addInfoAssessor,
            'historyAddInfoAssessor': historyAddInfoAssessor,
            'refreshTimeStamp': refreshTimeStamp,
            'assessorInfo': assessorEmail,
            'assessorStatus': assessorMode,
            'can_user_edit': can_user_edit,
            'docs_url': docs_url,
            'proposalId': proposalId,
            'applicationType': applicationType,
            'proposalLodgementDate': proposalLodgementDate
        }
    },
    getVisibility(h,c,readonly,assessor_mode,assessor_can_assess){
        var _status = {
            'visible':true,
            'editable':true
        }
        if (assessor_mode){
            if (c.isVisibleForAssessorOnly){
                if (this.status_data.can_user_edit){
                    _status.visible = false;
                }
                if (!assessor_can_assess){ _status.editable = false }
                return _status;
            }
            else {
                _status.editable = readonly ? false : true;
                _status.editable = readonly ? false : true;
            }
        }
        else{
            if (c.isVisibleForAssessorOnly){
                _status.visible = false;
                _status.editable = false;
            }
            else{
                _status.editable = readonly ? false : true;
            }
        }
        return _status;
    },
    generateCommentTextBoxes(h,c,val,assessor_mode,comment_data,assessor_info, comment_val){
        var box_visibility = this.status_data.assessorStatus.assessor_box_view
        var boxes = [];
        var assessor_visibility;
        var referral_name = '';
        var referral_visibility
        var referral_label = '';
        var name = '';
        if (!this.status_data.can_user_edit){
            if (comment_data){
                var _dt = undefined;
                if(comment_data.constructor != Object){
                    _dt = comment_data.find(at => at.name == c.name)
                }
                //var _dt = comment_data.find(at => at.name == c.name)
                // Assessor Data
                var assessor_name = `${c.name}-comment-field-Assessor`;
                //var assessor_val = _dt == undefined || _dt.assessor == '' ? '' : _dt.assessor;
                var assessor_val=null;
                //console.log(_dt)
                if(_dt==undefined)
                {
                    //if comment_data is dictionary instead of array (eg. comment data for old Proposal without referral comment functionality)
                    if(comment_data.constructor == Object){
                        //console.log('here', comment_val)
                        assessor_val= comment_val
                    }
                }
                else{
                    assessor_val = _dt.assessor == '' ? '' : _dt.assessor;
                }
                assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                assessor_visibility = !assessor_visibility;
                boxes.push(
                    {
                        "box_view": box_visibility,
                        "name": assessor_name,
                        "value": assessor_val,
                        //"label": "Deficiency assessor JM1",
                        "label": "Assessor (Deficiency comments)",
                        "readonly": assessor_visibility,
                        "question": c.label,
                        "referral_box": false,
                        "box_class": "form-control deficiency"
                    }

                    //<AssessorText box_view={box_visibility} type="text" name={assessor_name} value={assessor_val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visibility}/>
                )
                // Referral Data
                var current_referral_present = false;
                //console.log(c.type, _dt)
                if (_dt != undefined){
                    $.each(_dt.referrals,(i,v)=> {
                        if (v.email == assessor_info.email){ current_referral_present = true; }
                        var readonly = v.email == assessor_info.email && assessor_mode == 'referral' && this.status_data.assessorStatus.assessor_can_assess ? false : true;
                        var referral_name = `${c.name}-comment-field-Referral-${v.email}`;
                        boxes.push(
                            {
                                "box_view": box_visibility,
                                "name": referral_name,
                                "value": v.value,
                                "label": v.full_name + ' (Suggested Deficiency)',
                                "readonly": readonly,
                                "question": c.label,
                                "referral_box": true,
                                "box_class": "form-control"
                            }
                            //<AssessorText box_view={box_visibility} type="text" name={referral_name} value={v.value} label={v.full_name} help_text={c.help_text} readonly={readonly}/>
                        )
                    });
                }
                if (assessor_mode == 'referral'){
                    if (!current_referral_present){
                        // Add Referral Box
                        referral_name = `${c.name}-comment-field-Referral-${assessor_info.email}`;
                        referral_visibility =  assessor_mode == 'referral' && this.status_data.assessorStatus.assessor_can_assess ? false : true ;
                        referral_label = `${assessor_info.name}`;
                        boxes.push(
                            {
                                "box_view": box_visibility,
                                "name": referral_name,
                                "label": referral_label + ' (Suggested Deficiency)',
                                "readonly": referral_visibility,
                                "question": c.label,
                                "referral_box": true,
                                "box_class": "form-control",
                            }
                            // <AssessorText box_view={box_visibility} type="text" name={referral_name} value={assessor_val} label={referral_label} readonly={referral_visibility}/>
                            //<AssessorText box_view={box_visibility} type="text" name={referral_name} label={referral_label} readonly={referral_visibility}/>
                        )
                    }
                }
            }
            else{
                if (assessor_mode == 'assessor'){
                    name = `${c.name}-comment-field-Assessor`;
                    assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                    assessor_visibility = !assessor_visibility;
                    boxes.push(
                        {
                                "box_view": box_visibility,
                                "name": name,
                                "label": "Assessor (Deficiency comments)",
                                "readonly": assessor_visibility,
                                //"value": val,
                                "value": '',
                                "question": c.label,
                                "referral_box": false,
                                "box_class": "form-control deficiency",
                        }
                        //<AssessorText box_view={box_visibility} type="text" name={name} value={val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visibility}/>
                    )
                }
                else if (assessor_mode == 'referral'){
                    //console.log('referral');
                    // Add Assessor Box
                    name = `${c.name}-comment-field-Assessor`;
                    assessor_visibility = assessor_mode != 'assessor' ? true : false;
                    boxes.push(
                        {
                                "box_view": box_visibility,
                                "name": name,
                                "label": "Assessor (Deficiency comments)",
                                "readonly": assessor_visibility,
                                //"value": val,
                                "value": '',
                                "question": c.label,
                                "referral_box": false,
                                "box_class": "form-control deficiency",
                        }
                        //<AssessorText box_view={box_visibility} type="text" name={name} value={val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visibility}/>
                    )
                    // Add Referral Box
                    referral_name = `${c.name}-comment-field-Referral-${assessor_info.email}`;
                    referral_visibility = assessor_mode != 'referral' ? true : false;
                    referral_label = `${assessor_info.name}`;
                    boxes.push(
                        {
                                "box_view": box_visibility,
                                "name": referral_name,
                                "label": referral_label + ' (Suggested Deficiency)',
                                "readonly": referral_visibility,
                                //"value": val,
                                "value": '',
                                "question": c.label,
                                "referral_box": true,
                                "box_class": "form-control",
                        }
                        //<AssessorText box_view={box_visibility} type="text" name={referral_name} value={val} label={referral_label} readonly={referral_visibility}/>
                    )
                }
            }
        }
        // if (boxes.length > 0){
        //     boxes = [<div class="row"> {boxes} </div>]
        // }
        return boxes;
    },
    generateAddInfoApplicantTextBoxes(h,c,val,assessor_mode,readonly,add_info_applicant){
        var box_visibility = true;
        var boxes = [];
        // var applicant_visibility;
            if (add_info_applicant){
                //var _dt = add_info_applicant.find(at => at.name == c.name)
                // Assessor Data
                var _dt = add_info_applicant;
                var applicant_name = `${c.name}-add-info-applicant`;
                var applicant_val = _dt == undefined || _dt == '' ? val : _dt;
                // applicant_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? false : true;
                // applicant_visibility = !applicant_visibility;
                boxes.push(
                    <AssessorText box_view={box_visibility} type="text" name={applicant_name} value={applicant_val} label={'Additional Information (proponent)'} help_text={c.help_text} readonly={readonly}/>
                )
            }
            else{
                    var name = `${c.name}-add-info-applicant`;
                    var blank_val=null;
                    // applicant_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? false : true;
                    // applicant_visibility = !applicant_visibility;
                    boxes.push(
                        <AssessorText box_view={box_visibility} type="text" name={name} value={blank_val} label={'Additional Information (proponent)'} help_text={c.help_text} readonly={readonly}/>
                    )                
            }
        if (boxes.length > 0){
            boxes = [<div class="row"> {boxes} </div>]
        }
        return boxes;
    },
    generateAddInfoAssessorTextBoxes(h,c,val,assessor_mode,add_info_assessor,){
        var box_visibility = this.status_data.assessorStatus.assessor_box_view
        var boxes = [];
        if (!this.status_data.can_user_edit){
            if (add_info_assessor){
                // var _dt = undefined;
                // if(add_info_assessor.constructor != Object){
                //     _dt = add_info_assessor.find(at => at.name == c.name)
                // }
                //var _dt = add_info_assessor.find(at => at.name == c.name)
                // Assessor Data
                var assessor_name = `${c.name}-add-info-Assessor`;
                //var assessor_val = _dt == undefined || _dt.assessor == '' ? '' : _dt.assessor;
                var assessor_val=add_info_assessor;
                //console.log(_dt)
                // if(_dt==undefined)
                // {
                //     //if add_info_assessor is dictionary instead of array (eg. comment data for old Proposal without referral comment functionality)
                //     if(add_info_assessor.constructor == Object){
                //         //console.log('here', comment_val)
                //         assessor_val= comment_val
                //     }
                // }
                // else{
                //     assessor_val = _dt.assessor == '' ? '' : _dt.assessor;
                // }
                // var assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                // assessor_visibility = !assessor_visibility;
                // var assessor_visibility_always=assessor_visibility;
                var assessor_visibility_always=true;
                boxes.push(
                    // {
                    //     "box_view": box_visibility,
                    //     "name": assessor_name,
                    //     "value": assessor_val,
                    //     "label": "Additional Info (assessor)",
                    //     "readonly": assessor_visibility,
                    //     "question": c.label,
                    //     "referral_box": false,
                    //     "box_class": "form-control deficiency"
                    // }

                    <AssessorText box_view={box_visibility} type="text" name={assessor_name} value={assessor_val} label={'Additional Information (assessor)'} help_text={c.help_text} readonly={assessor_visibility_always}/>
                )
                // Referral Data
                // var current_referral_present = false;
                
                
            }
            // else{
            //     if (assessor_mode == 'assessor'){
            //         var name = `${c.name}-add-info-Assessor`;
            //         var assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
            //         assessor_visibility = !assessor_visibility;
            //         boxes.push(
            //             // {
            //             //         "box_view": box_visibility,
            //             //         "name": name,
            //             //         "label": "Additional Info (assessor)",
            //             //         "readonly": assessor_visibility,
            //             //         //"value": val,
            //             //         "value": '',
            //             //         "question": c.label,
            //             //         "referral_box": false,
            //             //         "box_class": "form-control deficiency",
            //             // }
            //             <AssessorText box_view={box_visibility} type="text" name={name} value={''} label={'Additional Info (assessor)'} help_text={c.help_text} readonly={assessor_visibility}/>
            //         )
            //     }
            //     else if (assessor_mode == 'referral'){
            //         //console.log('referral');
            //         // Add Assessor Box
            //         var name = `${c.name}-add-info-Assessor`;
            //         var assessor_visibility = assessor_mode != 'assessor' ? true : false;
            //         boxes.push(
            //             // {
            //             //         "box_view": box_visibility,
            //             //         "name": name,
            //             //         "label": "Additional Info (assessor)",
            //             //         "readonly": assessor_visibility,
            //             //         //"value": val,
            //             //         "value": '',
            //             //         "question": c.label,
            //             //         "referral_box": false,
            //             //         "box_class": "form-control deficiency",
            //             // }
            //             <AssessorText box_view={box_visibility} type="text" name={name} value={''} label={'Additional Info (assessor)'} help_text={c.help_text} readonly={assessor_visibility}/>
            //         )
            //     }
            // }
        }
        if (boxes.length > 0){
            boxes = [<div class="row"> {boxes} </div>]
        }
        return boxes;
    },
    generateHistoryAddInfoAssessorTextBoxes(h,c,val,assessor_mode,add_info_assessor,){
        var box_visibility = this.status_data.assessorStatus.assessor_box_view
        var boxes = [];
        if (!this.status_data.can_user_edit){
            if (add_info_assessor){
                // var _dt = undefined;
                // if(add_info_assessor.constructor != Object){
                //     _dt = add_info_assessor.find(at => at.name == c.name)
                // }
                //var _dt = add_info_assessor.find(at => at.name == c.name)
                // Assessor Data
                var assessor_name = `${c.name}-history-add-info-Assessor`;
                //var assessor_val = _dt == undefined || _dt.assessor == '' ? '' : _dt.assessor;
                var assessor_val=add_info_assessor;
                //console.log(_dt)
                // if(_dt==undefined)
                // {
                //     //if add_info_assessor is dictionary instead of array (eg. comment data for old Proposal without referral comment functionality)
                //     if(add_info_assessor.constructor == Object){
                //         //console.log('here', comment_val)
                //         assessor_val= comment_val
                //     }
                // }
                // else{
                //     assessor_val = _dt.assessor == '' ? '' : _dt.assessor;
                // }
                // var assessor_visibility = assessor_mode == 'assessor' && this.status_data.assessorStatus.has_assessor_mode && !this.status_data.assessorStatus.status_without_assessor? true : false;
                // assessor_visibility = !assessor_visibility;
                var assessor_visibility_always=true;
                boxes.push(
                    // {
                    //     "box_view": box_visibility,
                    //     "name": assessor_name,
                    //     "value": assessor_val,
                    //     "label": "Additional Info (assessor)",
                    //     "readonly": assessor_visibility,
                    //     "question": c.label,
                    //     "referral_box": false,
                    //     "box_class": "form-control deficiency"
                    // }

                    <AssessorText box_view={box_visibility} type="text" name={assessor_name} value={assessor_val} label={'History Additional Information (assessor)'} help_text={c.help_text} readonly={assessor_visibility_always}/>
                )
                // Referral Data
                // var current_referral_present = false;
                
                
            }
        }
        if (boxes.length > 0){
            boxes = [<div class="row"> {boxes} </div>]
        }
        return boxes;
    },
}
