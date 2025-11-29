# 代码更新说明

## 已根据实际 tianji Java 项目调整的内容

### 1. 接口路径更新

已根据实际的 Controller 接口路径更新了 `services/java_client.py`：

#### 原假设路径 → 实际路径

- ❌ `/learning/users/{userId}/profile` 
- ✅ `/lessons/page` (通过课表接口获取用户学习画像)

- ❌ `/trade/users/{userId}/courses`
- ✅ `/lessons/page` (课表即代表已购买课程)

- ❌ `/learning/users/{userId}/records`
- ✅ `/learning-records/course/{courseId}` (需要先有courseId)

- ❌ `/internal/courses/export`
- ✅ `/courses/page` (分页获取，status=2表示已上架)

- ❌ `/courses/{courseId}`
- ✅ `/course/{id}?withCatalogue=true&withTeachers=false` (内部接口)

### 2. 数据结构适配

#### 用户学习画像
- 使用 `/lessons/page` 返回的 `LearningLessonVO` 列表
- 包含：课程ID、课程名称、状态、已学章节数、总章节数等

#### 学习记录
- 使用 `/learning-records/course/{courseId}` 返回的 `LearningLessonDTO`
- 包含：课表ID、最近学习的小节ID、学习记录列表

#### 课程详情
- 使用 `/course/{id}` 返回的 `CourseFullInfoDTO`
- 注意：`CourseFullInfoDTO` 不包含课程介绍、适用人群、课程详情等字段
- 这些字段在 `CourseContent` 表中，可能需要额外查询

### 3. 需要进一步处理的问题

#### 问题1: 课程内容信息缺失

`CourseFullInfoDTO` 中没有以下字段：
- `courseIntroduce` (课程介绍)
- `usePeople` (适用人群)  
- `courseDetail` (课程详情)

**解决方案**:
1. 如果Java端有获取课程内容的接口，需要额外调用
2. 或者修改 `data_sync.py` 中的 `_build_course_document` 方法，只使用 `CourseFullInfoDTO` 中已有的字段
3. 或者建议Java端在 `CourseFullInfoDTO` 中包含这些字段

#### 问题2: 用户认证

大部分接口需要JWT Token认证。

**解决方案**:
1. 如果Python服务作为内部服务，配置内部服务认证token
2. 在 `JavaServiceClient` 中添加认证头
3. 或者通过网关配置允许内部服务访问

#### 问题3: 用户ID传递

`/lessons/page` 接口可能不直接接受 `userId` 参数，而是从认证信息中获取。

**解决方案**:
1. 如果接口支持 `userId` 参数，当前代码已处理
2. 如果不支持，需要：
   - 为每个用户创建临时token
   - 或者创建内部接口支持指定userId查询
   - 或者修改接口支持管理员查询任意用户的课表

### 4. 建议的Java端改进

为了更好支持AI助手，建议在Java端添加以下接口：

#### 1. 内部课程导出接口
```java
@GetMapping("/internal/courses/export")
public List<CourseFullInfoWithContentDTO> exportAllCourses() {
    // 返回所有已上架课程的完整信息（包括内容）
}
```

#### 2. 用户学习画像接口
```java
@GetMapping("/internal/users/{userId}/learning-profile")
public UserLearningProfileDTO getUserLearningProfile(@PathVariable Long userId) {
    // 返回用户的学习画像（包括学习时长、习惯、卡点等）
}
```

#### 3. 批量获取课程内容接口
```java
@PostMapping("/internal/courses/content/batch")
public Map<Long, CourseContentDTO> getCourseContents(@RequestBody List<Long> courseIds) {
    // 批量获取课程内容信息
}
```

### 5. 当前代码状态

✅ **已完成**:
- 接口路径已更新为实际路径
- 数据结构已适配实际返回格式
- 分页逻辑已实现
- 错误处理已添加

⚠️ **待完善**:
- 用户认证token处理
- 课程内容信息获取（如果需要）
- 用户ID传递方式确认

### 6. 下一步操作

1. **测试接口连接**
   - 确认Java服务地址和端口
   - 测试接口是否可访问

2. **处理认证**
   - 配置内部服务token
   - 或创建内部接口

3. **完善数据获取**
   - 确认课程内容是否需要额外获取
   - 根据实际情况调整数据同步逻辑

4. **测试数据同步**
   - 启动Python服务
   - 观察数据同步日志
   - 检查RAG知识库数据

