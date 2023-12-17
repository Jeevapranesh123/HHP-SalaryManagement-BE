async def get_employee_with_salary_details(employee_id, month):
    if isinstance(employee_id, str):
        employee_id = [employee_id]

    GET_EMPLOYEE_WITH_ALL_SALARY_DETAILS = [
        {"$match": {"employee_id": {"$in": employee_id}}},
        {
            "$lookup": {
                "from": "salary",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_info",
                "let": {"employee_id": "$employee_id", "targetDate": month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employee_id"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                ]
                            }
                        }
                    }
                ],
            }
        },
        {
            "$lookup": {
                "from": "monthly_compensation",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "monthly_compensation_info",
                "let": {"employee_id": "$employee_id", "targetDate": month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employee_id"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                ]
                            }
                        }
                    }
                ],
            }
        },
        {
            "$lookup": {
                "from": "loan_schedule",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "loan_schedule_info",
                "let": {"employee_id": "$employee_id", "targetMonth": month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employee_id"]},
                                    {"$eq": ["$month", "$$targetMonth"]},
                                ]
                            }
                        }
                    },
                    {"$group": {"_id": "$month", "sum": {"$sum": "$amount"}}},
                ],
            }
        },
        {
            "$lookup": {
                "from": "salary_advance",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_advance_info",
                "let": {"employeeId": "$employee_id", "targetDate": month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employeeId"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                    {"$eq": ["$status", "approved"]},
                                ]
                            }
                        }
                    },
                    {"$group": {"_id": "$month", "sum": {"$sum": "$amount"}}},
                ],
            }
        },
        {
            "$lookup": {
                "from": "salary_incentives",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_incentives_info",
                "let": {"employeeId": "$employee_id", "targetDate": month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employeeId"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                ]
                            }
                        }
                    }
                ],
            }
        },
        {
            "$addFields": {
                "salary": {"$arrayElemAt": ["$salary_info", 0]},
                "monthly_compensation": {
                    "$arrayElemAt": ["$monthly_compensation_info", 0]
                },
                "salary_advance": {"$arrayElemAt": ["$salary_advance_info", 0]},
                "loan": {"$arrayElemAt": ["$loan_schedule_info", 0]},
                "salary_incentives": {"$arrayElemAt": ["$salary_incentives_info", 0]},
            }
        },
        {
            "$addFields": {
                "gross_salary": {"$ifNull": ["$salary.gross_salary", 0]},
                "pf": {"$ifNull": ["$salary.pf", 0]},
                "esi": {"$ifNull": ["$salary.esi", 0]},
                "loss_of_pay": {"$ifNull": ["$monthly_compensation.loss_of_pay", 0]},
                "leave_cashback": {
                    "$ifNull": ["$monthly_compensation.leave_cashback", 0]
                },
                "last_year_leave_cashback": {
                    "$ifNull": ["$monthly_compensation.last_year_leave_cashback", 0]
                },
                "attendance_special_allowance": {
                    "$ifNull": ["$monthly_compensation.attendance_special_allowance", 0]
                },
                "other_special_allowance": {
                    "$ifNull": ["$monthly_compensation.other_special_allowance", 0]
                },
                "overtime": {"$ifNull": ["$monthly_compensation.overtime", 0]},
                "salary_advance": {"$ifNull": ["$salary_advance.sum", 0]},
                "loan": {"$ifNull": ["$loan.sum", 0]},
                "allowance": {"$ifNull": ["$salary_incentives.allowance", 0]},
                "increment": {"$ifNull": ["$salary_incentives.increment", 0]},
                "bonus": {"$ifNull": ["$salary_incentives.bonus", 0]},
            }
        },
        {
            "$project": {
                "salary_info": 0,
                "monthly_compensation_info": 0,
                "salary_incentives_info": 0,
                "salary": 0,
                "monthly_compensation": 0,
                "salary_incentives": 0,
                "loan_schedule_info": 0,
                "salary_advance_info": 0,
            }
        },
        {
            "$addFields": {
                "net_salary": {
                    "$subtract": [
                        {
                            "$add": [
                                "$gross_salary",
                                "$attendance_special_allowance",
                                "$leave_cashback",
                                "$last_year_leave_cashback",
                                "$other_special_allowance",
                                "$overtime",
                                "$allowance",
                                "$increment",
                                "$bonus",
                            ]
                        },
                        {
                            "$add": [
                                "$pf",
                                "$esi",
                                "$loss_of_pay",
                                "$salary_advance",
                                "$loan",
                            ]
                        },
                    ]
                }
            }
        },
    ]

    return GET_EMPLOYEE_WITH_ALL_SALARY_DETAILS


async def get_increment_report(start_date, end_date):
    return [
        {
            "$match": {
                "increment": {"$ne": 0},
                "month": {"$gte": start_date, "$lte": end_date},
            }
        },
        {"$sort": {"month": 1}},
        {
            "$project": {
                "_id": 0,
                "month": {"$dateToString": {"format": "%B", "date": "$month"}},
                "employee_id": "$employee_id",
                "amount": "$increment",
                "posted_at": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                },
                "posted_by": "$created_by",
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
    ]


async def get_bonus_report(start_date, end_date):
    return [
        {
            "$match": {
                "bonus": {"$ne": 0},
                "month": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        },
        {"$sort": {"month": 1}},
        {
            "$project": {
                "_id": 0,
                "month": {"$dateToString": {"format": "%B", "date": "$month"}},
                "employee_id": "$employee_id",
                "amount": "$bonus",
                "posted_at": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                },
                "posted_by": "$created_by",
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
    ]


async def get_allowance_report(start_date, end_date):
    return [
        {
            "$match": {
                "allowance": {"$ne": 0},
                "month": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        },
        {"$sort": {"month": 1}},
        {
            "$project": {
                "_id": 0,
                "month": {"$dateToString": {"format": "%B", "date": "$month"}},
                "employee_id": "$employee_id",
                "amount": "$allowance",
                "posted_at": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                },
                "posted_by": "$created_by",
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
    ]


async def get_attendance_special_allowance_report(start_date, end_date):
    return [
        {
            "$match": {
                "attendance_special_allowance": {"$ne": 0},
                "month": {"$gte": start_date, "$lte": end_date},
            }
        },
        {"$sort": {"month": 1}},
        {
            "$project": {
                "_id": 0,
                "month": {"$dateToString": {"format": "%B", "date": "$month"}},
                "employee_id": "$employee_id",
                "amount": "$attendance_special_allowance",
                "posted_at": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                },
                "posted_by": "$created_by",
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
    ]


async def get_other_special_allowance_report(start_date, end_date):
    return [
        {
            "$match": {
                "other_special_allowance": {"$ne": 0},
                "month": {"$gte": start_date, "$lte": end_date},
            }
        },
        {"$sort": {"month": 1}},
        {
            "$project": {
                "_id": 0,
                "month": {"$dateToString": {"format": "%B", "date": "$month"}},
                "employee_id": "$employee_id",
                "amount": "$other_special_allowance",
                "posted_at": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                },
                "posted_by": "$created_by",
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
    ]


async def get_leave_report(start_date, end_date):
    return [
        {"$sort": {"month": 1}},
        {
            "$match": {
                "leave_type": {"$ne": "permission"},
                "status": "approved",
                "month": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
        {
            "$project": {
                "_id": 0,
                "employee_id": 1,
                "name": 1,
                "leave_type": 1,
                "month": {"$dateToString": {"format": "%d-%m-%Y", "date": "$month"}},
                "start_date": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$start_date"}
                },
                "end_date": {
                    "$dateToString": {"format": "%d-%m-%Y", "date": "$end_date"}
                },
                "no_of_days": 1,
                "status": 1,
                "reason": 1,
                "remarks": 1,
                "approved_by": "$approved_or_rejected_by",
            }
        },
    ]


async def get_permission_report(start_date, end_date):
    return [
        {"$sort": {"date": 1}},
        {
            "$match": {
                "leave_type": "permission",
                "status": "approved",
                "month": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info",
            }
        },
        {"$addFields": {"employee_info": {"$arrayElemAt": ["$employee_info", 0]}}},
        {"$addFields": {"name": "$employee_info.name"}},
        {
            "$project": {
                "_id": 0,
                "employee_id": 1,
                "name": 1,
                "leave_type": 1,
                "month": {"$dateToString": {"format": "%d-%m-%Y", "date": "$month"}},
                "date": {"$dateToString": {"format": "%d-%m-%Y", "date": "$date"}},
                "start_time": {
                    "$dateToString": {"format": "%H:%M:%S", "date": "$start_time"}
                },
                "end_time": {
                    "$dateToString": {"format": "%H:%M:%S", "date": "$end_time"}
                },
                "no_of_hours": 1,
                "status": 1,
                "reason": 1,
                "remarks": 1,
                "approved_by": "$approved_or_rejected_by",
            }
        },
    ]
