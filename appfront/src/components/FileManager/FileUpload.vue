<template>
    <div class="upload" >
        <div style="">
            <el-upload class="upload-demo"
                action=""
                :multiple="true"
                :file-list="fileList"
                :http-request="submitUpload"
                >
                <el-button size="small" type="primary">上传文件</el-button>
            </el-upload>
        </div>
    </div>
</template>

<script>
import * as api from '../../assets/js/api'
export default {
    components:{
    },
    name:"upload",
    data() {
        return {
            name: "上传文件",
            fileList:[],
            formData:""
        }
    },
    methods: {
        submitUpload(file) {
            console.log("submitUpload");
            this.formData = new FormData()
            this.formData.append('upload', file.file);
            let config = {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
            this.axios.post("http://127.0.0.1:8000/filemanager/fileupload", this.formData, config).then(res => {
                    console.log(res) 
                    this.fileList = []
                    api.getMetaInfo().then(data => {
                        console.log(data.data.data)
                        this.$emit("listenToChild",data.data.data)
                    })
                })
                .catch( res => {
                    console.log(res)
                })
        },
    },
}
</script>

<style>
</style>
