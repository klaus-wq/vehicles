# def assign_drivers(self, vehicles, drivers):
#     active = extra = 0
#
#     pool = drivers[:]
#     random.shuffle(pool)
#
#     for i in range(0, len(vehicles), 10):
#         if i >= len(vehicles) or not pool: break
#         v = vehicles[i]
#         if DriverVehicle.objects.filter(vehicle=v, is_active=True).exists(): continue
#
#         d = pool.pop()
#         DriverVehicle.objects.create(driver=d, vehicle=v, is_active=True)
#         active += 1
#
#     max_e = min(3, max(1, len(vehicles) // 3))
#     for d in drivers:
#         for _ in range(random.randint(1, max_e)):
#             v = random.choice(vehicles)
#             if not DriverVehicle.objects.filter(driver=d, vehicle=v).exists():
#                 DriverVehicle.objects.create(driver=d, vehicle=v, is_active=False)
#                 extra += 1
#
#     return active, extra