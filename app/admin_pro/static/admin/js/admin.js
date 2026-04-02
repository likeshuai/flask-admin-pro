/**
 * Flask Admin Pro - Main JavaScript Application
 */

// Global Vue app instance
const { createApp, ref, reactive, onMounted } = Vue;

// Page-specific components
const pageComponents = {
    // Dashboard component
    dashboard: {
        data() {
            return {
                stats: { user_count: 0, model_count: 0, request_count: 0, error_rate: 0 }
            };
        },
        methods: {
            goTo(path) {
                window.location.href = path;
            },
            async loadStats() {
                try {
                    // Load user count
                    const usersRes = await fetch('/__admin__/api/users?page=1&per_page=1');
                    const usersData = await usersRes.json();
                    this.stats.user_count = usersData.total || 0;
                    
                    // Load model count  
                    const modelsRes = await fetch('/__admin__/api/models');
                    const modelsData = await modelsRes.json();
                    this.stats.model_count = modelsData.models?.length || 0;
                    
                    // Load monitor stats
                    const monitorRes = await fetch('/__admin__/api/monitor/stats?range=24');
                    const monitorData = await monitorRes.json();
                    this.stats.request_count = monitorData.total_requests || 0;
                    this.stats.error_rate = monitorData.error_rate || 0;
                    
                } catch (error) {
                    console.error('Failed to load stats:', error);
                }
            }
        },
        async mounted() {
            await this.loadStats();
        }
    },
    
    // Users management component
    users: {
        data() {
            return {
                loading: false,
                submitting: false,
                users: [],
                page: 1,
                perPage: 20,
                total: 0,
                search: '',
                dialogVisible: false,
                isEdit: false,
                editingUser: null,
                form: {
                    username: '',
                    email: '',
                    password: '',
                    role: 'admin',
                    is_active: true
                },
                rules: {
                    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
                    email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }]
                }
            };
        },
        methods: {
            async loadUsers() {
                this.loading = true;
                try {
                    const response = await fetch(`/__admin__/api/users?page=${this.page}&per_page=${this.perPage}&search=${this.search}`);
                    const data = await response.json();
                    this.users = data.data || [];
                    this.total = data.total || 0;
                } catch (error) {
                    ElementPlus.ElMessage.error('加载用户列表失败');
                } finally {
                    this.loading = false;
                }
            },
            showCreate() {
                this.isEdit = false;
                this.editingUser = null;
                this.form.username = '';
                this.form.email = '';
                this.form.password = '';
                this.form.role = 'admin';
                this.form.is_active = true;
                this.dialogVisible = true;
            },
            showEdit(user) {
                this.isEdit = true;
                this.editingUser = user;
                this.form.username = user.username;
                this.form.email = user.email || '';
                this.form.password = '';
                this.form.role = user.role;
                this.form.is_active = user.is_active;
                this.dialogVisible = true;
            },
            async submit() {
                this.submitting = true;
                try {
                    const formData = { ...this.form };
                    if (this.isEdit && !formData.password) {
                        delete formData.password;
                    }
                    
                    const response = await fetch(
                        this.isEdit ? `/__admin__/api/users/${this.editingUser.id}` : '/__admin__/api/users',
                        {
                            method: this.isEdit ? 'PUT' : 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(formData)
                        }
                    );
                    
                    const result = await response.json();
                    if (result.success) {
                        ElementPlus.ElMessage.success(this.isEdit ? '用户更新成功' : '用户创建成功');
                        this.dialogVisible = false;
                        this.loadUsers();
                    } else {
                        ElementPlus.ElMessage.error(result.error || '操作失败');
                    }
                } catch (error) {
                    ElementPlus.ElMessage.error('网络错误');
                } finally {
                    this.submitting = false;
                }
            },
            async handleDelete(user) {
                try {
                    await ElementPlus.ElMessageBox.confirm(
                        `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
                        '确认删除',
                        {
                            confirmButtonText: '确定',
                            cancelButtonText: '取消',
                            type: 'warning'
                        }
                    );
                    
                    const response = await fetch(`/__admin__/api/users/${user.id}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        ElementPlus.ElMessage.success('用户删除成功');
                        this.loadUsers();
                    } else {
                        ElementPlus.ElMessage.error(result.error || '删除失败');
                    }
                } catch (error) {
                    // User cancelled
                }
            }
        },
        async mounted() {
            await this.loadUsers();
        }
    },
    
    // Models list component
    models: {
        data() {
            return {
                loading: false,
                models: []
            };
        },
        methods: {
            async loadModels() {
                this.loading = true;
                try {
                    const response = await fetch('/__admin__/api/models');
                    const data = await response.json();
                    
                    // Get record count for each model
                    const modelsWithCount = [];
                    for (const model of data.models || []) {
                        try {
                            const countResponse = await fetch(`/__admin__/api/models/${model.name}?page=1&per_page=1`);
                            const countData = await countResponse.json();
                            modelsWithCount.push({
                                ...model,
                                record_count: countData.total || 0
                            });
                        } catch (error) {
                            modelsWithCount.push({ ...model, record_count: 0 });
                        }
                    }
                    
                    this.models = modelsWithCount;
                } catch (error) {
                    ElementPlus.ElMessage.error('加载模型列表失败');
                } finally {
                    this.loading = false;
                }
            },
            refreshModels() {
                this.loadModels();
            },
            goToModel(modelName) {
                window.location.href = `/__admin__/model/${modelName}`;
            }
        },
        async mounted() {
            await this.loadModels();
        }
    },
    
    // Monitor component
    monitor: {
        data() {
            return {
                loading: false,
                stats: {},
                logs: [],
                page: 1,
                perPage: 50,
                total: 0
            };
        },
        methods: {
            async loadStats() {
                try {
                    const response = await fetch('/__admin__/api/monitor/stats?range=24');
                    const data = await response.json();
                    this.stats = data;
                } catch (error) {
                    console.error('Failed to load stats:', error);
                }
            },
            async loadLogs() {
                this.loading = true;
                try {
                    const response = await fetch(`/__admin__/api/monitor/logs?page=${this.page}&per_page=${this.perPage}`);
                    const data = await response.json();
                    this.logs = data.logs || [];
                    this.total = data.total || 0;
                } catch (error) {
                    ElementPlus.ElMessage.error('加载日志失败');
                } finally {
                    this.loading = false;
                }
            },
            getMethodType(method) {
                const types = { GET: '', POST: 'success', PUT: 'warning', DELETE: 'danger' };
                return types[method] || '';
            },
            getStatusType(code) {
                if (code >= 200 && code < 300) return 'success';
                if (code >= 400) return 'danger';
                return 'info';
            }
        },
        async mounted() {
            await this.loadStats();
            await this.loadLogs();
        }
    }
};

// Initialize the main Vue app
const app = createApp({
    setup() {
        const currentRoute = ref(window.location.pathname.replace('/__admin__', '') || '/');
        const userMenuVisible = ref(false);
        const user = reactive(window.adminPageConfig.user || {});
        
        const showUserMenu = () => {
            userMenuVisible.value = !userMenuVisible.value;
        };
        
        const logout = async () => {
            try {
                await fetch('/__admin__/api/logout', { method: 'POST' });
                window.location.href = '/__admin__/login';
            } catch (e) {
                ElementPlus.ElMessage.error('退出失败');
            }
        };
        
        const handleThemeChange = (theme) => {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('admin-theme', theme);
            ElementPlus.ElMessage.success('主题已切换');
        };
        
        // Load saved theme
        onMounted(() => {
            const savedTheme = localStorage.getItem('admin-theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-theme', savedTheme);
            }
        });
        
        return {
            currentRoute,
            userMenuVisible,
            user,
            showUserMenu,
            logout,
            handleThemeChange
        };
    }
});

// Mount page-specific components
document.addEventListener('DOMContentLoaded', function() {
    app.use(ElementPlus).mount('#app');
    
    // Mount additional page components if they exist
    const routeMap = {
        'admin.index': 'dashboard',
        'admin.users': 'users', 
        'admin.models': 'models',
        'admin.monitor': 'monitor'
    };
    
    const currentPage = window.adminPageConfig.route;
    const componentName = routeMap[currentPage];
    
    if (componentName && pageComponents[componentName]) {
        // For pages that need additional functionality beyond the base layout
        // This can be extended as needed
    }
});
