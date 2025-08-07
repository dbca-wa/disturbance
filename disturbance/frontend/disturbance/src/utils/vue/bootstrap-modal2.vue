<template id="bootstrap-modal">
    <!-- minor changes from bootstrap-modal.vue to allow multiple modals on same calling component -->
    <div v-show="show" :transition="transition" :showModal="showModal" modal_id="modal_id">
        <!--{{show}}-->
        <div class="modal" @click.self="clickMask">
            <div class="modal-dialog" :class="modalClass" role="document">
                <div class="modal-content">
                    <!--Header-->
                    <slot name="header">
                        <div class="modal-header">
                            <a type="button" class="close" @click="cancel">x</a>
                            <h4 class="modal-title">
                                <slot name="title">
                                    {{title}}
                                </slot>
                            </h4>
                        </div>
                    </slot>
                    <!--Container-->
                    <div class="modal-body">
                        <slot></slot>
                    </div>
                    <!--Footer-->
                    <div class="modal-footer">
                        <slot name="footer">
                            <button id="okBtn" type="button" :class="okClass" @click="ok" :disabled="okButtonDisabled">{{okText}}</button>
                            <button type="button" :class="cancelClass" @click="cancel">{{cancelText}}</button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-backdrop in"></div>
    </div>
</template>

<script>
    /**
     * Bootstrap Style Modal Component for Vue
     * Depend on Bootstrap.css
     */

     export default {
        props: {
            title: {
                type: String,
                default: 'Modal'
            },
            small: {
                type: Boolean,
                default: false
            },
            large: {
                type: Boolean,
                default: true
            },
            xlarge: {
                type: Boolean,
                default: false
            },
            xxlarge: {
                type: Boolean,
                default: false
            },
            full: {
                type: Boolean,
                default: false
            },
            force: {
                type: Boolean,
                default: false
            },
            transition: {
                type: String,
                default: 'modal'
            },
            okText: {
                type: String,
                default: 'OK'
            },
            cancelText: {
                type: String,
                default: 'Cancel'
            },
            okClass: {
                type: String,
                default: 'btn btn-default'
            },
            cancelClass: {
                type: String,
                default: 'btn btn-default'
            },
            closeWhenOK: {
                type: Boolean,
                default: false
            },
            showModal: {
                type: Boolean,
                default: false
            },
            modal_id: {
                type: String,
                default: 'Cancel'
            },
        },
        data () {
            return {
                duration: null,
                okButtonDisabled: false,
            };
        },
        computed: {
            modalClass () {
                return {
                    'modal-xxl': this.xxlarge,
                    'modal-xl': this.xlarge,
                    'modal-lg': this.large,
                    'modal-sm': this.small,
                    'modal-full': this.full
                }
            },
//            show: function() {
//                return this.$parent.isModalOpen;
//            },
            show: function() {
                return this.showModal;
            }
        },
        created () {
            if (this.show) {
                document.body.className += ' modal-open';
            }
        },
        beforeUnmount () {
            document.body.className = document.body.className.replace(/\s?modal-open/, '');
        },
        watch: {
            show (value) {
                if (value) {
                    document.body.className += ' modal-open';
                }
                else {

                    window.setTimeout(() => {
                        document.body.className = document.body.className.replace(/\s?modal-open/, '');
                    }, this.duration || 0);
                }
            },
        },
        methods: {
            ok () {
                this.$emit('ok');
                if (this.closeWhenOK) {
                    this.show = false;
                }
            },
            cancel () {
                console.log('cancel-'+this.modal_id)
                this.$emit('cancel');
                this.$parent.close(this.modal_id);
            },
            clickMask () {
                if (!this.force) {
                    this.cancel();
                }
            }
        }
     };
</script>


<style scoped>
    .modal {
        display: block;
    }
    .modal .btn {
        margin-bottom: 0px;
    }
    .modal-header {
        border-top-left-radius: .3rem;
        border-top-right-radius: .3rem;
    }
    .modal-footer{
        border-bottom-left-radius: .3rem;
        border-bottom-right-radius: .3rem;
    }
    .modal-body, .modal-footer, .modal-header {
        /*background-color: #F5F5F5;
        color: #333333;*/
        background-color: #efefef;
        color: #333333;
    }
    .modal-transition {
        transition: all .6s ease;
    }
    .modal-leave {
        border-radius: 1px !important;
    }
    .modal-transition .modal-dialog, .modal-transition .modal-backdrop {
        transition: all .5s ease;
    }
    .modal-enter .modal-dialog, .modal-leave .modal-dialog {
        opacity: 0;
        transform: translateY(-30%);
    }
    .modal-enter .modal-backdrop, .modal-leave .modal-backdrop {
        opacity: 0;
    }
    .close {
        font-size: 2.5rem;
        opacity: .3;
    }
    .close:hover {
        opacity: .7;
    }
    #okBtn {
        margin-bottom: 0px;
    }

    @media (min-width: 992px) {
      .modal-dialog {
	width: 600px;
	margin: 30px auto;
      }
      .modal-content {
	-webkit-box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
	box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
      }
      .modal-sm {
	width: 300px;
      }
      .modal-md {
	width: 810px;
      }
      .modal-lg {
	width: 900px;
      }
      .modal-xl {
	width: 990px;
      }
      .modal-xxl {
	width: 1080px;
      }
    }

/*
    @media (min-width: 992px) {
      .modal-lg {
	width: 900px;
      }
      .modal-xl {
	width: 80%;
      }
      .modal-xxl {
	width: 95%;
      }
    }
*/

</style>
