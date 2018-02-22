import raftos


loop.create_task(
    raftos.register(
        # node running on this machine
        '127.0.0.1:8000',

        # other servers
        cluster=[
            '127.0.0.1:8001',
            '127.0.0.1:8002'
        ]
    )
)
loop.run_forever()
