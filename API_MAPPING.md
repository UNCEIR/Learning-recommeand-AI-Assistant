# Java接口映射说明

本文档说明 Python AI Assistant 如何调用 tianji Java 项目的实际接口。

## 接口路径映射

### 1. 用户学习画像

**Python调用**: `get_user_learning_profile(user_id)`

**实际Java接口**: `GET /lessons/page`

**说明**: 
- 通过"我的课表"接口获取用户的学习情况
- 返回用户的课表列表，包含课程状态、学习进度等信息
- 需要传递 `userId` 参数（如果接口支持）或通过认证信息获取

**返回数据结构**:
```json
{
  "list": [
    {
      "id": 1,
      "courseId": 100,
      "courseName": "Java多线程",
      "status": 1,  // 0-未学习，1-学习中，2-已学完，3-已失效
      "learnedSections": 5,
      "sections": 10,
      "latestSectionName": "线程同步",
      ...
    }
  ],
  "total": 10
}
```

### 2. 用户购买课程

**Python调用**: `get_user_purchased_courses(user_id)`

**实际Java接口**: `GET /lessons/page`

**说明**: 
- 课表即代表已购买的课程
- 与学习画像使用同一接口，但只返回课程列表

### 3. 用户学习记录

**Python调用**: `get_user_learning_records(user_id, course_id)`

**实际Java接口**: `GET /learning-records/course/{courseId}`

**说明**: 
- 获取指定课程的学习记录
- 需要先有 courseId，如果没有则从课表中获取

**返回数据结构**:
```json
{
  "id": 1,
  "latestSectionId": 5,
  "records": [
    {
      "id": 1,
      "sectionId": 1,
      "moment": 300,  // 观看时间点（秒）
      "finished": true,
      "finishTime": "2025-11-25T10:00:00"
    }
  ]
}
```

### 4. 获取所有课程（数据预热）

**Python调用**: `get_all_courses()`

**实际Java接口**: `GET /courses/page`

**说明**: 
- 分页获取所有已上架课程（status=2）
- 用于RAG知识库数据预热

**参数**:
- `page`: 页码
- `size`: 每页大小
- `status`: 2（已上架）

### 5. 获取课程详情

**Python调用**: `get_course_detail(course_id)`

**实际Java接口**: `GET /course/{id}?withCatalogue=true&withTeachers=false`

**说明**: 
- 内部接口，获取课程完整信息
- `withCatalogue=true` 获取目录信息
- `withTeachers=false` 不获取老师信息（减少数据量）

**返回数据结构**:
```json
{
  "id": 100,
  "name": "Java多线程",
  "courseIntroduce": "课程介绍...",
  "usePeople": "适用人群...",
  "courseDetail": "课程详情...",
  "catalogue": [
    {
      "id": 1,
      "name": "第一章",
      "type": 1,  // 1-章，2-节，3-测试
      "children": [...]
    }
  ],
  ...
}
```

## 注意事项

### 1. 用户认证

**重要**: 大部分接口需要用户认证（JWT Token）

**解决方案**:
- 如果Python服务作为内部服务调用，可能需要：
  1. 配置内部服务认证token
  2. 或者通过网关配置允许内部服务访问
  3. 或者创建专门的内网接口

### 2. 接口路径前缀

根据实际部署情况，可能需要调整：
- `JAVA_SERVICE_BASE_URL`: Java服务的基础URL
- `JAVA_SERVICE_API_PREFIX`: API路径前缀（如 `/api`）

### 3. 数据格式

Java接口返回的数据格式可能包含：
- `R<T>` 包装类：实际数据在 `data` 字段中
- `PageDTO<T>` 分页数据：包含 `list` 和 `total` 字段

代码中已处理这些情况。

### 4. 需要创建的内部接口

为了支持数据预热，建议在Java端创建一个内部接口：

```java
@GetMapping("/internal/courses/export")
public List<CourseFullInfoDTO> exportAllCourses() {
    // 返回所有已上架课程的完整信息
    // 包括课程内容、目录等
}
```

或者使用现有的 `/courses/page` 接口分页获取（代码已实现）。

## 接口调用示例

### 获取用户课表
```http
GET /api/lessons/page?userId=1&size=100
Authorization: Bearer <token>
```

### 获取课程学习记录
```http
GET /api/learning-records/course/100
Authorization: Bearer <token>
```

### 获取所有课程（分页）
```http
GET /api/courses/page?page=1&size=100&status=2
Authorization: Bearer <token>
```

### 获取课程详情
```http
GET /api/course/100?withCatalogue=true&withTeachers=false
Authorization: Bearer <token>
```

