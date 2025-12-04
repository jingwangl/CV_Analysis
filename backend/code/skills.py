# -*- coding: utf-8 -*-
"""
技能关键词库 - 统一管理所有技能关键词
"""

# 技能关键词列表（小写格式，用于匹配）
SKILL_KEYWORDS = [
    # ========== 编程语言 ==========
    # 主流语言
    "java", "python", "go", "golang", "c++", "cpp", "c", "javascript", "js", "typescript", "ts",
    "c#", "csharp", "rust", "php", "ruby", "swift", "kotlin", "scala", "r语言", "r", "perl", "lua",
    # 其他语言
    "dart", "objective-c", "objc", "matlab", "shell", "bash", "powershell", "groovy", "clojure",
    "erlang", "elixir", "haskell", "f#", "fsharp", "ocaml", "prolog", "fortran", "cobol",
    
    # ========== 前端技术 ==========
    # 框架和库
    "react", "vue", "vue.js", "angular", "angularjs", "svelte", "next.js", "nextjs", "nuxt.js", "nuxtjs",
    "ember", "backbone", "knockout", "mobx", "redux", "zustand", "recoil", "jotai",
    # UI库和组件
    "jquery", "bootstrap", "ant design", "antd", "element ui", "element-ui", "element plus",
    "material-ui", "mui", "vuetify", "quasar", "primevue", "tailwind css", "tailwindcss",
    "sass", "scss", "less", "stylus", "css3", "html5", "webpack", "vite", "rollup", "parcel",
    # 前端工具
    "babel", "eslint", "prettier", "jest", "mocha", "cypress", "playwright", "puppeteer",
    "storybook", "d3.js", "d3", "three.js", "threejs", "chart.js", "echarts",
    
    # ========== 后端框架 ==========
    # Java生态
    "spring", "springboot", "spring boot", "spring mvc", "spring cloud", "spring security",
    "mybatis", "mybatis-plus", "hibernate", "struts", "jpa", "jdbc", "servlet", "jsp",
    "netty", "vert.x", "play framework", "akka", "spark java",
    # Python生态
    "django", "flask", "fastapi", "tornado", "bottle", "sanic", "aiohttp", "asyncio",
    "celery", "gunicorn", "uwsgi", "wsgi", "asgi",
    # Node.js生态
    "node.js", "nodejs", "node", "express", "koa", "nest.js", "nestjs", "hapi", "sails",
    "meteor", "adonis", "loopback", "feathers",
    # 其他后端
    "laravel", "rails", "ruby on rails", "gin", "echo", "fiber", "beego", "iris",
    "asp.net", "aspnet", "dotnet", ".net", "dotnet core", "entity framework", "ef",
    "phoenix", "plug", "cowboy",
    
    # ========== 数据库 ==========
    # 关系型数据库
    "mysql", "mariadb", "postgresql", "postgres", "oracle", "sql server", "mssql", "sqlite",
    "db2", "informix", "sybase", "teradata", "greenplum",
    # NoSQL数据库
    "mongodb", "mongo", "redis", "cassandra", "hbase", "couchdb", "couchbase",
    "dynamodb", "neo4j", "arangodb", "orientdb", "influxdb", "timescaledb",
    # 搜索引擎
    "elasticsearch", "es", "solr", "lucene", "opensearch",
    # 数据仓库
    "hive", "impala", "presto", "clickhouse", "druid", "kylin",
    
    # ========== 消息队列和中间件 ==========
    "kafka", "rabbitmq", "rocketmq", "activemq", "pulsar", "nats", "zeromq", "zmq",
    "redis stream", "redis pub/sub", "nsq", "beanstalkd",
    
    # ========== 缓存 ==========
    "redis", "memcached", "hazelcast", "ehcache", "caffeine", "guava cache",
    
    # ========== 工具和平台 ==========
    # 容器化
    "docker", "containerd", "podman", "kubernetes", "k8s", "k3s", "helm", "istio",
    "linkerd", "consul", "etcd", "zookeeper",
    # CI/CD
    "jenkins", "gitlab ci", "github actions", "travis ci", "circleci", "teamcity",
    "bamboo", "azure devops", "ci/cd", "cicd", "gitops", "argo cd", "argo",
    # 版本控制
    "git", "svn", "mercurial", "perforce",
    # 构建工具
    "maven", "gradle", "ant", "sbt", "npm", "yarn", "pnpm", "pip", "conda",
    # 云平台
    "aws", "amazon web services", "azure", "gcp", "google cloud", "阿里云", "alibaba cloud",
    "腾讯云", "tencent cloud", "华为云", "huawei cloud", "ucloud", "七牛云", "qiniu",
    "aws ec2", "aws s3", "aws lambda", "aws ecs", "aws eks", "aws rds", "aws dynamodb",
    "azure functions", "azure app service", "gcp compute", "gcp cloud functions",
    # 服务器和操作系统
    "linux", "ubuntu", "centos", "redhat", "rhel", "debian", "fedora", "suse",
    "windows server", "unix", "freebsd", "openbsd",
    # Web服务器
    "nginx", "apache", "apache httpd", "tomcat", "jetty", "undertow", "iis",
    # 监控和日志
    "prometheus", "grafana", "elk", "elasticsearch", "logstash", "kibana", "splunk",
    "datadog", "new relic", "apm", "jaeger", "zipkin", "skywalking", "pinpoint",
    
    # ========== 网络协议和技术 ==========
    "tcp/ip", "tcp", "udp", "http", "https", "http/2", "http2", "http/3", "http3",
    "websocket", "ws", "wss", "grpc", "graphql", "rest", "restful", "soap",
    "mqtt", "coap", "amqp", "stomp", "dns", "dhcp", "ftp", "sftp", "ssh", "telnet",
    "tls", "ssl", "ipv4", "ipv6", "ospf", "bgp", "vpn", "sdn", "nfv",
    
    # ========== 系统和技术概念 ==========
    "多线程", "multithreading", "并发", "concurrency", "并行", "parallelism",
    "网络编程", "network programming", "socket编程", "socket programming",
    "jvm", "jre", "jdk", "gc", "garbage collection", "内存管理", "memory management",
    "sql优化", "sql optimization", "数据库优化", "database optimization",
    "性能优化", "performance optimization", "性能调优", "performance tuning",
    "缓存", "cache", "缓存策略", "caching strategy",
    "负载均衡", "load balancing",  "high availability", "ha",
    "容灾", "disaster recovery", "备份", "backup", "恢复", "recovery",
    "安全", "security", "加密", "encryption", "认证", "authentication", "授权", "authorization",
    "oauth", "oauth2", "jwt", "token", "saml", "ldap", "单点登录", "sso",
    "设计模式", "design pattern", "架构设计", "architecture design",
    "微服务", "microservices", "服务治理", "service governance",
    "分布式", "distributed", "分布式系统", "distributed systems",
    "高并发", "high concurrency", "高吞吐", "high throughput",
    "消息队列", "message queue", "事件驱动", "event driven",
    "领域驱动设计", "ddd", "domain driven design",
    "测试驱动开发", "tdd", "test driven development",
    "敏捷开发", "agile", "scrum", "kanban", "devops", "sre",
    
    # ========== AI/ML ==========
    "机器学习", "machine learning", "ml", "深度学习", "deep learning", "dl",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "paddlepaddle", "mxnet", "caffe", "caffe2", "theano", "torch",
    "nlp", "自然语言处理", "natural language processing",
    "计算机视觉", "computer vision", "cv", "图像处理", "image processing",
    "cnn", "rnn", "lstm", "gru", "transformer", "bert", "gpt", "attention",
    "gan", "生成对抗网络", "reinforcement learning", "强化学习", "rl",
    "opencv", "pillow", "numpy", "pandas", "matplotlib", "seaborn",
    "xgboost", "lightgbm", "catboost", "spark mllib", "h2o",
    
    # ========== 大数据 ==========
    "hadoop", "hdfs", "mapreduce", "yarn", "spark", "spark streaming",
    "flink", "storm", "samza", "beam", "airflow", "oozie",
    "hive", "pig", "sqoop", "flume", "kafka", "zookeeper",
    
    # ========== 移动开发 ==========
    "android", "ios", "react native", "reactnative", "flutter", "xamarin",
    "ionic", "cordova", "phonegap", "uniapp", "uni-app",
    "swift", "objective-c", "kotlin", "java", "dart",
    
    # ========== 游戏开发 ==========
    "unity", "unreal engine", "cocos2d", "godot", "phaser",
    
    # ========== 区块链 ==========
    "blockchain", "区块链", "ethereum", "solidity", "hyperledger", "fabric",
    "bitcoin", "智能合约", "smart contract",
    
    # ========== 其他技术 ==========
    "api", "rpc", "sdk", "webservice", "中间件", "middleware",
    "搜索引擎", "search engine", "推荐系统", "recommendation system",
    "实时计算", "real-time computing", "流式计算", "stream computing",
    "数据挖掘", "data mining", "数据分析", "data analysis",
    "商业智能", "bi", "business intelligence", "数据可视化", "data visualization",
    "etl", "数据仓库", "data warehouse", "数据湖", "data lake",
    "项目管理", "project management", "jira", "confluence", "trello", "asana",
    "代码审查", "code review", "持续集成", "continuous integration",
    "持续部署", "continuous deployment", "持续交付", "continuous delivery"
]


def get_skill_keywords_lowercase():
    """返回小写格式的技能列表（用于匹配）"""
    return SKILL_KEYWORDS


def get_skill_keywords_titlecase():
    """返回首字母大写格式的技能列表（用于显示）"""
    result = []
    for skill in SKILL_KEYWORDS:
        # 处理特殊格式
        if skill == "c++" or skill == "cpp":
            result.append("C++")
        elif skill == "c#":
            result.append("C#")
        elif skill == "csharp":
            result.append("C#")
        elif skill == "node.js" or skill == "nodejs":
            result.append("Node.js")
        elif skill == "node":
            result.append("Node")
        elif skill == "ci/cd" or skill == "cicd":
            result.append("CI/CD")
        elif skill == "tcp/ip":
            result.append("TCP/IP")
        elif skill == "sql server" or skill == "mssql":
            result.append("SQL Server")
        elif skill == "sql优化":
            result.append("SQL优化")
        elif skill == "r语言" or skill == "r":
            result.append("R语言")
        elif skill == "js":
            result.append("JavaScript")
        elif skill == "ts":
            result.append("TypeScript")
        elif skill == "golang" or skill == "go":
            result.append("Go")
        elif skill == "vue.js" or skill == "vuejs":
            result.append("Vue.js")
        elif skill == "next.js" or skill == "nextjs":
            result.append("Next.js")
        elif skill == "nuxt.js" or skill == "nuxtjs":
            result.append("Nuxt.js")
        elif skill == "nest.js" or skill == "nestjs":
            result.append("Nest.js")
        elif skill == "spring boot" or skill == "springboot":
            result.append("Spring Boot")
        elif skill == "spring mvc":
            result.append("Spring MVC")
        elif skill == "spring cloud":
            result.append("Spring Cloud")
        elif skill == "spring security":
            result.append("Spring Security")
        elif skill == "mybatis-plus":
            result.append("MyBatis-Plus")
        elif skill == "ruby on rails":
            result.append("Ruby on Rails")
        elif skill == "asp.net" or skill == "aspnet":
            result.append("ASP.NET")
        elif skill == ".net" or skill == "dotnet":
            result.append(".NET")
        elif skill == "dotnet core":
            result.append(".NET Core")
        elif skill == "entity framework" or skill == "ef":
            result.append("Entity Framework")
        elif skill == "react native" or skill == "reactnative":
            result.append("React Native")
        elif skill == "uni-app" or skill == "uniapp":
            result.append("uni-app")
        elif skill == "unreal engine":
            result.append("Unreal Engine")
        elif skill == "tailwind css" or skill == "tailwindcss":
            result.append("Tailwind CSS")
        elif skill == "material-ui" or skill == "mui":
            result.append("Material-UI")
        elif skill == "element ui" or skill == "element-ui":
            result.append("Element UI")
        elif skill == "element plus":
            result.append("Element Plus")
        elif skill == "ant design" or skill == "antd":
            result.append("Ant Design")
        elif skill == "d3.js" or skill == "d3":
            result.append("D3.js")
        elif skill == "three.js" or skill == "threejs":
            result.append("Three.js")
        elif skill == "chart.js":
            result.append("Chart.js")
        elif skill == "gitlab ci":
            result.append("GitLab CI")
        elif skill == "github actions":
            result.append("GitHub Actions")
        elif skill == "travis ci":
            result.append("Travis CI")
        elif skill == "azure devops":
            result.append("Azure DevOps")
        elif skill == "amazon web services":
            result.append("Amazon Web Services")
        elif skill == "google cloud" or skill == "gcp":
            result.append("Google Cloud")
        elif skill == "alibaba cloud":
            result.append("Alibaba Cloud")
        elif skill == "tencent cloud":
            result.append("Tencent Cloud")
        elif skill == "huawei cloud":
            result.append("Huawei Cloud")
        elif skill == "aws ec2":
            result.append("AWS EC2")
        elif skill == "aws s3":
            result.append("AWS S3")
        elif skill == "aws lambda":
            result.append("AWS Lambda")
        elif skill == "aws ecs":
            result.append("AWS ECS")
        elif skill == "aws eks":
            result.append("AWS EKS")
        elif skill == "aws rds":
            result.append("AWS RDS")
        elif skill == "aws dynamodb":
            result.append("AWS DynamoDB")
        elif skill == "azure functions":
            result.append("Azure Functions")
        elif skill == "azure app service":
            result.append("Azure App Service")
        elif skill == "gcp compute":
            result.append("GCP Compute")
        elif skill == "gcp cloud functions":
            result.append("GCP Cloud Functions")
        elif skill == "windows server":
            result.append("Windows Server")
        elif skill == "apache httpd":
            result.append("Apache HTTPD")
        elif skill == "http/2" or skill == "http2":
            result.append("HTTP/2")
        elif skill == "http/3" or skill == "http3":
            result.append("HTTP/3")
        elif skill == "scikit-learn" or skill == "sklearn":
            result.append("Scikit-learn")
        elif skill == "machine learning" or skill == "ml":
            result.append("Machine Learning")
        elif skill == "deep learning" or skill == "dl":
            result.append("Deep Learning")
        elif skill == "natural language processing" or skill == "nlp":
            result.append("Natural Language Processing")
        elif skill == "computer vision" or skill == "cv":
            result.append("Computer Vision")
        elif skill == "image processing":
            result.append("Image Processing")
        elif skill == "reinforcement learning" or skill == "rl":
            result.append("Reinforcement Learning")
        elif skill == "generative adversarial network" or skill == "gan":
            result.append("GAN")
        elif skill == "domain driven design" or skill == "ddd":
            result.append("Domain Driven Design")
        elif skill == "test driven development" or skill == "tdd":
            result.append("Test Driven Development")
        elif skill == "business intelligence" or skill == "bi":
            result.append("Business Intelligence")
        elif skill == "data warehouse":
            result.append("Data Warehouse")
        elif skill == "data lake":
            result.append("Data Lake")
        elif skill == "data visualization":
            result.append("Data Visualization")
        elif skill == "data analysis":
            result.append("Data Analysis")
        elif skill == "data mining":
            result.append("Data Mining")
        elif skill == "recommendation system":
            result.append("Recommendation System")
        elif skill == "search engine":
            result.append("Search Engine")
        elif skill == "real-time computing":
            result.append("Real-time Computing")
        elif skill == "stream computing":
            result.append("Stream Computing")
        elif skill == "continuous integration":
            result.append("Continuous Integration")
        elif skill == "continuous deployment":
            result.append("Continuous Deployment")
        elif skill == "continuous delivery":
            result.append("Continuous Delivery")
        elif skill == "code review":
            result.append("Code Review")
        elif skill == "project management":
            result.append("Project Management")
        elif skill == "load balancing":
            result.append("Load Balancing")
        elif skill == "high availability" or skill == "ha":
            result.append("High Availability")
        elif skill == "disaster recovery":
            result.append("Disaster Recovery")
        elif skill == "performance optimization":
            result.append("Performance Optimization")
        elif skill == "performance tuning":
            result.append("Performance Tuning")
        elif skill == "caching strategy":
            result.append("Caching Strategy")
        elif skill == "service governance":
            result.append("Service Governance")
        elif skill == "high concurrency":
            result.append("High Concurrency")
        elif skill == "high throughput":
            result.append("High Throughput")
        elif skill == "message queue":
            result.append("Message Queue")
        elif skill == "event driven":
            result.append("Event Driven")
        elif skill == "design pattern":
            result.append("Design Pattern")
        elif skill == "architecture design":
            result.append("Architecture Design")
        elif skill == "distributed systems":
            result.append("Distributed Systems")
        elif skill == "network programming":
            result.append("Network Programming")
        elif skill == "socket programming":
            result.append("Socket Programming")
        elif skill == "memory management":
            result.append("Memory Management")
        elif skill == "database optimization":
            result.append("Database Optimization")
        elif skill == "sql optimization":
            result.append("SQL Optimization")
        elif skill == "multithreading":
            result.append("Multithreading")
        elif skill == "concurrency":
            result.append("Concurrency")
        elif skill == "parallelism":
            result.append("Parallelism")
        elif skill == "garbage collection" or skill == "gc":
            result.append("Garbage Collection")
        elif "/" in skill or skill.isupper() or any('\u4e00' <= c <= '\u9fff' for c in skill):
            # 包含中文或已经是全大写的，保持原样
            result.append(skill)
        else:
            # 首字母大写（处理多词的情况）
            if " " in skill:
                # 多词技能，每个词首字母大写
                result.append(" ".join(word.capitalize() for word in skill.split()))
            else:
                result.append(skill.capitalize())
    return result

